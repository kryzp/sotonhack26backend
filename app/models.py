from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

import enum

class GameMode(str, enum.Enum):
	TEAM = "team"
	INDIVIDUAL = "individual"

class GameStatus(str, enum.Enum):
	WAITING = "waiting"
	IN_PROGRESS = "in_progress"
	FINISHED = "finished"

class RoundStatus(str, enum.Enum):
	PENDING = "pending"
	WORDS_GENERATED = "words_generated"
	BUZZ_OPEN = "buzz_open"
	BUZZ_LOCKED = "buzz_locked"
	SIDE_SELECTED = "side_selected"
	ANSWERING = "answering"
	VALIDATING = "validating"
	FIRST_RESOLVED = "first_resolved"
	SECOND_SIDE_SELECTED = "second_side_selected"
	SECOND_ANSWERING = "second_answering"
	SECOND_VALIDATING = "second_validating"
	RESOLVED = "resolved"

class SelectedSide(str, enum.Enum):
	LEFT = "left"
	RIGHT = "right"

class Round(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	game_id: int = Field(foreign_key="game.id", index=True)
	round_number: int
	word_one: Optional[str] = None
	word_two: Optional[str] = None
	status: str = Field(default=RoundStatus.PENDING.value)
	buzz_open: bool = False
	buzz_locked: bool = False
	buzzed_player: Optional[str] = None # player name
	buzzed_at: Optional[str] = None # ISO timestamp
	selected_side: Optional[str] = None # left | right
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
	game: Optional["Game"] = Relationship(back_populates="rounds")

class Game(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	mode: str = Field(default=GameMode.TEAM.value)
	difficulty: str = Field(default="medium")
	total_rounds: int = 3
	current_round_number: int = 0
	status: str = Field(default=GameStatus.WAITING.value)
	team_left_name: str = Field(default="Team Left")
	team_right_name: str = Field(default="Team Right")
	team_left_score: int = 0
	team_right_score: int = 0
	winner: Optional[str] = None
	created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
	rounds: List[Round] = Relationship(back_populates="game")
