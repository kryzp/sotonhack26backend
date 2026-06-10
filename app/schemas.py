from typing import Optional, List
from pydantic import BaseModel


class CreateGameRequest(BaseModel):
	rounds: int = 3
	mode: str = "team" # team | individual
	difficulty: str = "medium" # easy | medium | hard | brutal
	team_left_name: str = "Team Left"
	team_right_name: str = "Team Right"


class BuzzRequest(BaseModel):
	player_id: str # player label / identifier
	timestamp: Optional[str] = None


class SelectSideRequest(BaseModel):
	side: str # left | right


class TranscriptRequest(BaseModel):
	transcript: str


class FinalAnswerRequest(BaseModel):
	answer: str


class ScoreUpdateRequest(BaseModel):
	side: str # left | right
	delta: int


class CommentaryRequest(BaseModel):
	event: str
	context: dict = {}


class RoundResponse(BaseModel):
	id: Optional[int] = None
	game_id: int
	round_number: int
	word_one: Optional[str] = None
	word_two: Optional[str] = None
	status: str
	buzz_open: bool
	buzz_locked: bool
	buzzed_player: Optional[str] = None
	buzzed_at: Optional[str] = None
	selected_side: Optional[str] = None
	raw_transcript: Optional[str] = None
	final_answer: Optional[str] = None
	validation_valid: Optional[bool] = None
	validation_score: Optional[float] = None
	validation_steps: Optional[int] = None
	validation_reason: Optional[str] = None
	points_awarded: int = 0
	second_selected_side: Optional[str] = None
	second_raw_transcript: Optional[str] = None
	second_final_answer: Optional[str] = None
	second_validation_valid: Optional[bool] = None
	second_validation_score: Optional[float] = None
	second_validation_steps: Optional[int] = None
	second_validation_reason: Optional[str] = None
	second_points_awarded: int = 0
	model_config = { "from_attributes": True }


class GameResponse(BaseModel):
	id: Optional[int] = None
	mode: str
	difficulty: str = "medium"
	total_rounds: int
	current_round_number: int
	status: str
	team_left_name: str = "Team Left"
	team_right_name: str = "Team Right"
	team_left_score: int
	team_right_score: int
	winner: Optional[str] = None
	created_at: str
	rounds: List[RoundResponse] = []
	model_config = { "from_attributes": True }


class ValidationResponse(BaseModel):
	valid: bool
	score: float
	steps: int
	short_reason: str
