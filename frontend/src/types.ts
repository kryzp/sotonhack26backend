export type Screen = 'menu' | 'tutorial' | 'skinSelection' | 'game' | 'results'

export type Difficulty = 'easy' | 'medium' | 'hard' | 'brutal'

export type GameSettings = {
  rounds: number
  difficulty: Difficulty
  timer: number
}

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

export type Player = {
  id: string
  name: string
  title: string
  color: string
}

export type PromptPair = {
  left: string
  right: string
}

export type RoundData = {
  id: number
  prompt: PromptPair
  transcript: string[]
  judgement: string
  awardedPlayerId: string
  awardedPoints: number
  cue: string
}

export type PlayerScore = Player & {
  score: number
}

export type RoundResponse = {
  id: number | null
  game_id: number
  round_number: number
  word_one: string | null
  word_two: string | null
  status: string
  buzz_open: boolean
  buzz_locked: boolean
  buzzed_player: string | null
  buzzed_at: string | null
  selected_side: string | null
  raw_transcript: string | null
  final_answer: string | null
  validation_valid: boolean | null
  validation_score: number | null
  validation_steps: number | null
  validation_reason: string | null
  points_awarded: number
  second_selected_side: string | null
  second_raw_transcript: string | null
  second_final_answer: string | null
  second_validation_valid: boolean | null
  second_validation_score: number | null
  second_validation_steps: number | null
  second_validation_reason: string | null
  second_points_awarded: number
}

export type GameResponse = {
  id: number | null
  mode: string
  difficulty: string
  total_rounds: number
  current_round_number: number
  status: string
  team_left_name: string
  team_right_name: string
  team_left_score: number
  team_right_score: number
  winner: string | null
  created_at: string
  rounds: RoundResponse[]
}