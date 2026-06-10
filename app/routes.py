from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.database import get_session
from app.schemas import (
	CreateGameRequest, BuzzRequest, SelectSideRequest,
	TranscriptRequest, FinalAnswerRequest, ScoreUpdateRequest,
	CommentaryRequest,
	GameResponse, RoundResponse,
)
from app import game_service
from app import tts_service
from app import commentary_templates
from app.ws_manager import manager
from urllib.parse import quote

router = APIRouter()

async def _broadcast_game(session: Session, game_id: int, event: str):
	game = game_service.get_game(session, game_id)
	payload = {
		"event": event,
		"game": GameResponse.model_validate(game).model_dump(),
	}
	await manager.broadcast(game_id, payload)


@router.get("/health")
def health():
	return {"status": "ok"}


@router.post("/games", response_model=GameResponse)
async def create_game(body: CreateGameRequest, session: Session = Depends(get_session)):
	game = game_service.create_game(
		session, body.rounds, body.mode,
		difficulty=body.difficulty,
		team_left_name=body.team_left_name,
		team_right_name=body.team_right_name,
	)
	await _broadcast_game(session, game.id, "game_created")
	return game


@router.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: int, session: Session = Depends(get_session)):
	return game_service.get_game(session, game_id)


@router.post("/games/{game_id}/start", response_model=GameResponse)
async def start_game(game_id: int, session: Session = Depends(get_session)):
	game = game_service.start_game(session, game_id)
	await _broadcast_game(session, game_id, "game_started")
	return game


@router.post("/games/{game_id}/next-round", response_model=RoundResponse)
async def next_round(game_id: int, session: Session = Depends(get_session)):
	rnd = game_service.next_round(session, game_id)
	await _broadcast_game(session, game_id, "round_started")
	return rnd


@router.get("/games/{game_id}/rounds/current", response_model=RoundResponse)
def current_round(game_id: int, session: Session = Depends(get_session)):
	return game_service.get_current_round(session, game_id)


@router.post("/games/{game_id}/rounds/current/open-buzz", response_model=RoundResponse)
async def open_buzz(game_id: int, session: Session = Depends(get_session)):
	rnd = game_service.open_buzz(session, game_id)
	await _broadcast_game(session, game_id, "buzz_opened")
	return rnd


@router.post("/games/{game_id}/rounds/current/buzz", response_model=RoundResponse)
async def buzz(game_id: int, body: BuzzRequest, session: Session = Depends(get_session)):
	rnd = game_service.buzz(session, game_id, body.player_id, body.timestamp)
	await _broadcast_game(session, game_id, "buzz_locked")
	return rnd


@router.post("/games/{game_id}/rounds/current/select-side", response_model=RoundResponse)
async def select_side(game_id: int, body: SelectSideRequest, session: Session = Depends(get_session)):
	rnd = game_service.select_side(session, game_id, body.side)
	await _broadcast_game(session, game_id, "side_selected")
	return rnd


@router.post("/games/{game_id}/rounds/current/transcript", response_model=RoundResponse)
async def submit_transcript(game_id: int, body: TranscriptRequest, session: Session = Depends(get_session)):
	rnd = game_service.submit_transcript(session, game_id, body.transcript)
	await _broadcast_game(session, game_id, "transcript_submitted")
	return rnd


@router.post("/games/{game_id}/rounds/current/final-answer", response_model=RoundResponse)
async def submit_final_answer(game_id: int, body: FinalAnswerRequest, session: Session = Depends(get_session)):
	rnd = game_service.submit_final_answer(session, game_id, body.answer)
	await _broadcast_game(session, game_id, "answer_edited")
	return rnd


@router.post("/games/{game_id}/rounds/current/validate", response_model=RoundResponse)
async def validate(game_id: int, session: Session = Depends(get_session)):
	rnd = game_service.validate_round(session, game_id)
	await _broadcast_game(session, game_id, "validation_completed")
	return rnd


@router.post("/games/{game_id}/rounds/current/second-transcript", response_model=RoundResponse)
async def submit_second_transcript(game_id: int, body: TranscriptRequest, session: Session = Depends(get_session)):
	rnd = game_service.submit_second_transcript(session, game_id, body.transcript)
	await _broadcast_game(session, game_id, "second_transcript_submitted")
	return rnd


@router.post("/games/{game_id}/rounds/current/second-final-answer", response_model=RoundResponse)
async def submit_second_final_answer(game_id: int, body: FinalAnswerRequest, session: Session = Depends(get_session)):
	rnd = game_service.submit_second_answer(session, game_id, body.answer)
	await _broadcast_game(session, game_id, "second_answer_edited")
	return rnd


@router.post("/games/{game_id}/rounds/current/validate-second", response_model=RoundResponse)
async def validate_second(game_id: int, session: Session = Depends(get_session)):
	rnd = game_service.validate_second_round(session, game_id)
	await _broadcast_game(session, game_id, "second_validation_completed")
	return rnd


@router.post("/games/{game_id}/update-score", response_model=GameResponse)
async def update_score(game_id: int, body: ScoreUpdateRequest, session: Session = Depends(get_session)):
	game = game_service.update_score(session, game_id, body.side, body.delta)
	await _broadcast_game(session, game_id, "score_changed")
	return game


@router.post("/games/{game_id}/commentary")
async def commentary(game_id: int, body: CommentaryRequest):
	text = commentary_templates.get_commentary(body.event, body.context)
	safe_text = quote(text, safe='')
	return StreamingResponse(
		tts_service.generate_speech_stream(text),
		media_type="audio/mpeg",
		headers={
			"X-Commentary-Text": safe_text,
			"Access-Control-Expose-Headers": "X-Commentary-Text",
		},
	)


@router.websocket("/ws/games/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int):
	await manager.connect(game_id, websocket)
	try:
		# Keep the connection alive; clients just listen for broadcasts
		while True:
			# We can optionally accept messages from clients here
			await websocket.receive_text()
	except WebSocketDisconnect:
		manager.disconnect(game_id, websocket)
