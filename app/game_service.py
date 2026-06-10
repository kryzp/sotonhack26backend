from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Game, Round, GameStatus, RoundStatus, GameMode
from app.config import POINTS_PER_CORRECT
from app import gemini_client

def _get_game(session: Session, game_id: int) -> Game:
	game = session.get(Game, game_id)
	if not game:
		raise HTTPException(status_code=404, detail="Game not found")
	return game


def _current_round(session: Session, game: Game) -> Round:
	stmt = select(Round).where(
		Round.game_id == game.id,
		Round.round_number == game.current_round_number,
	)

	rnd = session.exec(stmt).first()
	
	if not rnd:
		raise HTTPException(status_code=404, detail="No current round")

	return rnd


def create_game(session: Session, total_rounds: int, mode: str, difficulty: str = "medium", team_left_name: str = "Team Left", team_right_name: str = "Team Right") -> Game:
	if total_rounds not in (1, 3, 5, 7, 9):
		raise HTTPException(status_code=400, detail="rounds must be 1, 3, 5, 7, or 9")

	if mode not in (GameMode.TEAM.value, GameMode.INDIVIDUAL.value):
		raise HTTPException(status_code=400, detail="mode must be 'team' or 'individual'")

	if difficulty not in ("easy", "medium", "hard", "brutal"):
		difficulty = "medium"

	game = Game(
		total_rounds=total_rounds,
		mode=mode,
		difficulty=difficulty,
		team_left_name=team_left_name,
		team_right_name=team_right_name,
	)
	session.add(game)
	session.commit()
	session.refresh(game)

	# Pre-generate words for all rounds to save API quota restrictions
	words_list = gemini_client.generate_words(amount=total_rounds)
	
	for i in range(total_rounds):
		pair = words_list[i] if i < len(words_list) else {"word_one": "error", "word_two": "fallback"}
		rnd = Round(
			game_id=game.id,
			round_number=i + 1,
			word_one=pair.get("word_one"),
			word_two=pair.get("word_two"),
			status=RoundStatus.PENDING.value,
		)
		session.add(rnd)

	session.commit()
	session.refresh(game)

	return game


def get_game(session: Session, game_id: int) -> Game:
	return _get_game(session, game_id)


def start_game(session: Session, game_id: int) -> Game:
	game = _get_game(session, game_id)
	
	if game.status != GameStatus.WAITING.value:
		raise HTTPException(status_code=400, detail="Game already started or finished")
	
	game.status = GameStatus.IN_PROGRESS.value
	
	session.add(game)
	session.commit()
	session.refresh(game)

	return game


def next_round(session: Session, game_id: int) -> Round:
	game = _get_game(session, game_id)

	if game.status == GameStatus.WAITING.value:
		raise HTTPException(status_code=400, detail="Start the game first")
	if game.status == GameStatus.FINISHED.value:
		raise HTTPException(status_code=400, detail="Game is already finished")

	# skip first round
	if game.current_round_number > 0:
		prev = _current_round(session, game)
		if prev.status != RoundStatus.RESOLVED.value:
			raise HTTPException(status_code=400, detail="Current round is not resolved yet")

	new_number = game.current_round_number + 1
	if new_number > game.total_rounds:
		raise HTTPException(status_code=400, detail="All rounds completed")

	# Fetch the pre-populated round from the database
	stmt = select(Round).where(
		Round.game_id == game.id,
		Round.round_number == new_number,
	)
	rnd = session.exec(stmt).first()

	if not rnd:
		raise HTTPException(status_code=500, detail="Round data missing")
		
	rnd.status = RoundStatus.WORDS_GENERATED.value
	session.add(rnd)

	game.current_round_number = new_number

	session.add(game)
	session.commit()
	session.refresh(rnd)
	session.refresh(game)

	return rnd


def get_current_round(session: Session, game_id: int) -> Round:
	game = _get_game(session, game_id)
	return _current_round(session, game)


def open_buzz(session: Session, game_id: int) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status not in (RoundStatus.WORDS_GENERATED.value,):
		raise HTTPException(status_code=400, detail="Cannot open buzz in current state")

	rnd.buzz_open = True
	rnd.buzz_locked = False
	rnd.status = RoundStatus.BUZZ_OPEN.value

	session.add(rnd)
	session.commit()
	session.refresh(rnd)

	return rnd


def buzz(session: Session, game_id: int, player_id: str, timestamp: Optional[str] = None) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if not rnd.buzz_open:
		raise HTTPException(status_code=400, detail="Buzz is not open")
	if rnd.buzz_locked:
		raise HTTPException(status_code=409, detail="Buzz already locked — someone else was faster")

	# lock the buzzer for the winning player
	rnd.buzz_locked = True
	rnd.buzzed_player = player_id
	rnd.buzzed_at = timestamp or datetime.now(timezone.utc).isoformat()
	rnd.status = RoundStatus.BUZZ_LOCKED.value

	session.add(rnd)
	session.commit()
	session.refresh(rnd)

	return rnd


def select_side(session: Session, game_id: int, side: str) -> Round:
	if side not in ("left", "right"):
		raise HTTPException(status_code=400, detail="side must be 'left' or 'right'")

	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status != RoundStatus.BUZZ_LOCKED.value:
		raise HTTPException(status_code=400, detail="Buzz must be locked before selecting side")

	rnd.selected_side = side
	rnd.status = RoundStatus.SIDE_SELECTED.value

	session.add(rnd)
	session.commit()
	session.refresh(rnd)

	return rnd


def submit_transcript(session: Session, game_id: int, transcript: str) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status not in (RoundStatus.SIDE_SELECTED.value, RoundStatus.ANSWERING.value):
		raise HTTPException(status_code=400, detail="Not in answering phase")

	rnd.raw_transcript = transcript
	rnd.status = RoundStatus.ANSWERING.value

	session.add(rnd)
	session.commit()
	session.refresh(rnd)

	return rnd


def submit_final_answer(session: Session, game_id: int, answer: str) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status not in (RoundStatus.SIDE_SELECTED.value, RoundStatus.ANSWERING.value):
		raise HTTPException(status_code=400, detail="Not in answering phase")

	rnd.final_answer = answer
	rnd.status = RoundStatus.ANSWERING.value

	session.add(rnd)
	session.commit()
	session.refresh(rnd)

	return rnd


def validate_round(session: Session, game_id: int) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status != RoundStatus.ANSWERING.value:
		raise HTTPException(status_code=400, detail="Not ready to validate")

	if not rnd.final_answer or not rnd.final_answer.strip():
		rnd.validation_valid = False
		rnd.validation_score = 0
		rnd.validation_steps = 0
		rnd.validation_reason = "No answer given."
		rnd.points_awarded = 0
	else:
		rnd.status = RoundStatus.VALIDATING.value
		session.add(rnd)
		session.commit()

		result = gemini_client.validate_answer(rnd.word_one, rnd.word_two, rnd.final_answer, game.difficulty)

		rnd.validation_valid = result.get("valid", False)
		rnd.validation_score = result.get("score", 0)
		rnd.validation_steps = result.get("steps", 0)
		rnd.validation_reason = result.get("short_reason", "")

	# Scoring: 1 point per step (lowest total wins)
	if rnd.validation_valid and rnd.selected_side:
		rnd.points_awarded = max(rnd.validation_steps or 1, 1)
		if rnd.selected_side == "left":
			game.team_left_score += rnd.points_awarded
		else:
			game.team_right_score += rnd.points_awarded
	elif rnd.selected_side:
		# Invalid answer: penalty of 10 steps
		rnd.points_awarded = 10
		if rnd.selected_side == "left":
			game.team_left_score += rnd.points_awarded
		else:
			game.team_right_score += rnd.points_awarded

	# Move to second player's turn (not fully resolved yet)
	rnd.status = RoundStatus.FIRST_RESOLVED.value
	# Auto-assign second player to opposite side
	rnd.second_selected_side = "right" if rnd.selected_side == "left" else "left"

	session.add(rnd)
	session.add(game)
	session.commit()
	session.refresh(rnd)
	session.refresh(game)

	return rnd


def submit_second_transcript(session: Session, game_id: int, transcript: str) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status not in (RoundStatus.FIRST_RESOLVED.value, RoundStatus.SECOND_SIDE_SELECTED.value, RoundStatus.SECOND_ANSWERING.value):
		raise HTTPException(status_code=400, detail="Not in second player answering phase")

	rnd.second_raw_transcript = transcript
	rnd.status = RoundStatus.SECOND_ANSWERING.value

	session.add(rnd)
	session.commit()
	session.refresh(rnd)

	return rnd


def submit_second_answer(session: Session, game_id: int, answer: str) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status not in (RoundStatus.FIRST_RESOLVED.value, RoundStatus.SECOND_SIDE_SELECTED.value, RoundStatus.SECOND_ANSWERING.value):
		raise HTTPException(status_code=400, detail="Not in second player answering phase")

	rnd.second_final_answer = answer
	rnd.status = RoundStatus.SECOND_ANSWERING.value

	session.add(rnd)
	session.commit()
	session.refresh(rnd)

	return rnd


def validate_second_round(session: Session, game_id: int) -> Round:
	game = _get_game(session, game_id)
	rnd = _current_round(session, game)

	if rnd.status != RoundStatus.SECOND_ANSWERING.value:
		raise HTTPException(status_code=400, detail="Not ready to validate second answer")

	if not rnd.second_final_answer or not rnd.second_final_answer.strip():
		rnd.second_validation_valid = False
		rnd.second_validation_score = 0
		rnd.second_validation_steps = 0
		rnd.second_validation_reason = "No answer given."
		rnd.second_points_awarded = 0
	else:
		rnd.status = RoundStatus.SECOND_VALIDATING.value
		session.add(rnd)
		session.commit()

		result = gemini_client.validate_answer(
			rnd.word_one, rnd.word_two, rnd.second_final_answer, game.difficulty,
			first_player_answer=rnd.final_answer,
		)

		rnd.second_validation_valid = result.get("valid", False)
		rnd.second_validation_score = result.get("score", 0)
		rnd.second_validation_steps = result.get("steps", 0)
		rnd.second_validation_reason = result.get("short_reason", "")

		overlap_penalty = result.get("overlap_penalty", 0)

		# Scoring: steps + 2 per overlapping step
		if rnd.second_validation_valid and rnd.second_selected_side:
			base_steps = max(rnd.second_validation_steps or 1, 1)
			rnd.second_points_awarded = base_steps + (overlap_penalty * 2)
			if overlap_penalty > 0:
				rnd.second_validation_reason = (
					f"{rnd.second_validation_reason} (+{overlap_penalty * 2} penalty for {overlap_penalty} shared steps)"
				)
		elif rnd.second_selected_side:
			# Invalid answer: penalty of 10 steps
			rnd.second_points_awarded = 10

	if rnd.second_selected_side:
		if not rnd.second_points_awarded and rnd.second_validation_valid:
			rnd.second_points_awarded = max(rnd.second_validation_steps or 1, 1)
		if rnd.second_selected_side == "left":
			game.team_left_score += rnd.second_points_awarded
		else:
			game.team_right_score += rnd.second_points_awarded

	rnd.status = RoundStatus.RESOLVED.value
	session.add(rnd)

	# check if the game is finished
	if game.current_round_number >= game.total_rounds:
		game.status = GameStatus.FINISHED.value
		# Lowest score wins!
		if game.team_left_score < game.team_right_score:
			game.winner = "left"
		elif game.team_right_score < game.team_left_score:
			game.winner = "right"
		else:
			game.winner = "tie"

	session.add(game)
	session.commit()
	session.refresh(rnd)
	session.refresh(game)

	return rnd


def update_score(session: Session, game_id: int, side: str, delta: int) -> Game:
	if side not in ("left", "right"):
		raise HTTPException(status_code=400, detail="side must be 'left' or 'right'")

	game = _get_game(session, game_id)

	if side == "left":
		game.team_left_score += delta
	else:
		game.team_right_score += delta

	session.add(game)
	session.commit()
	session.refresh(game)

	return game
