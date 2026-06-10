import { useState, useEffect, useRef } from 'react'
import ImagePlaceholder from './ImagePlaceholder'
import type { GameResponse, RoundResponse } from '../types'
import type { TurnPhase } from '../App'

const tableSrc = '/placeholders/table.png'
const remoteSrc = '/placeholders/remote.png'

type Props = {
  game: GameResponse
  round: RoundResponse
  teamLeftName: string
  teamRightName: string
  teamLeftSkin: string
  teamRightSkin: string
  secondsLeft: number
  maxSeconds: number
  liveSentence: string
  roundAnnouncement: string
  lastSubmittedSentence: string
  isSpeaking: boolean
  isAnswering: boolean
  pendingRoundAdvance: boolean
  isProcessing: boolean
  turnPhase: TurnPhase
  firstPlayerAnswer: string
  onBuzz: (side: 'left' | 'right') => void
  onSubmit: () => void
  onForceEnd: () => void
  onLiveSentenceChange: (value: string) => void
}

export default function GameStage({
  game,
  round,
  teamLeftName,
  teamRightName,
  teamLeftSkin,
  teamRightSkin,
  secondsLeft,
  liveSentence,
  roundAnnouncement,
  lastSubmittedSentence,
  isSpeaking,
  isAnswering,
  pendingRoundAdvance,
  isProcessing,
  turnPhase,
  firstPlayerAnswer,
  onBuzz,
  onSubmit,
  onForceEnd,
  onLiveSentenceChange,
}: Props) {
  const leftHolding = round.selected_side === 'left' && (turnPhase === 'first_player' || turnPhase === 'between_turns')
  const rightHolding = round.selected_side === 'right' && (turnPhase === 'first_player' || turnPhase === 'between_turns')
  const secondLeftHolding = round.second_selected_side === 'left' && turnPhase === 'second_player'
  const secondRightHolding = round.second_selected_side === 'right' && turnPhase === 'second_player'
  const anyHolding = leftHolding || rightHolding || secondLeftHolding || secondRightHolding
  const remoteGrabbed = anyHolding
  const wordOne = round.word_one || '???'
  const wordTwo = round.word_two || '???'

  const currentAnsweringSide = turnPhase === 'second_player' ? round.second_selected_side : round.selected_side
  const currentAnsweringName = currentAnsweringSide === 'left' ? teamLeftName : teamRightName

  const [teleporting, setTeleporting] = useState<'left' | 'right' | null>(null)
  const prevSideRef = useRef(round.selected_side)

  useEffect(() => {
    if (round.selected_side && !prevSideRef.current) {
      setTeleporting(round.selected_side as 'left' | 'right')
      const t1 = setTimeout(() => {
        setTeleporting(null)
      }, 800)
      return () => {
        clearTimeout(t1)
      }
    }
    prevSideRef.current = round.selected_side
  }, [round.selected_side])

  const leftHidden = teleporting === 'left'
  const rightHidden = teleporting === 'right'

  const showBuzzButtons = turnPhase === 'buzzer_open' && round.buzz_open && !round.buzz_locked

  const showDialogue = turnPhase === 'first_player' || turnPhase === 'second_player'

  return (
    <div className="stage">
      {teleporting && <div className="impact-overlay" />}
      <div className="stage-banner">
        <div className="stage-banner__words">
          <span className="stage-banner__word stage-banner__word--left">{wordOne}</span>
          <span className="stage-banner__vs">connect to</span>
          <span className="stage-banner__word stage-banner__word--right">{wordTwo}</span>
        </div>
        <div className={`stage-banner__timer ${secondsLeft <= 5 ? 'stage-banner__timer--urgent' : ''}`}>
          {isAnswering ? secondsLeft : ''}
        </div>
      </div>

      {/* Info area: below words, above characters */}
      <div className="stage-centre-ui">
        {/* Waiting for presenter / buzzer */}
        {(turnPhase === 'presenting' || turnPhase === 'waiting_buzzer') && (
          <div className="stage-announcement">
            {turnPhase === 'presenting' ? 'Listen up...' : 'Get ready...'}
          </div>
        )}

        {/* Buzz area */}
        {showBuzzButtons && (
          <div className="stage-buzz">
            <button className="stage-buzz__btn" onClick={() => onBuzz('left')} disabled={isProcessing}>
              {teamLeftName}
            </button>
            <span className="stage-buzz__label">GRAB IT!</span>
            <button className="stage-buzz__btn" onClick={() => onBuzz('right')} disabled={isProcessing}>
              {teamRightName}
            </button>
          </div>
        )}

        {/* Show first player's answer during second player's turn */}
        {turnPhase === 'second_player' && firstPlayerAnswer && !pendingRoundAdvance && (
          <div className="stage-judgement" style={{ opacity: 0.7 }}>
            <div className="stage-judgement__verdict">Player 1's answer (avoid these steps!):</div>
            <div className="stage-judgement__reason" style={{ fontStyle: 'italic' }}>
              "{firstPlayerAnswer}"
            </div>
          </div>
        )}

        {/* Transcript text */}
        {showDialogue && (
          <div className="stage-dialogue">
            <div className="stage-dialogue__speaker">
              {isSpeaking ? `${currentAnsweringName} is answering...` : 'Statement'}
            </div>
            <textarea
              className="stage-dialogue__input"
              placeholder="Type your connection here..."
              value={liveSentence}
              onChange={(e) => onLiveSentenceChange(e.target.value)}
              disabled={!isAnswering || pendingRoundAdvance || isProcessing}
              rows={3}
            />
            {isAnswering && !pendingRoundAdvance && (
              <button className="stage-dialogue__submit" onClick={onSubmit} disabled={isProcessing || !liveSentence.trim()}>
                Submit
              </button>
            )}
          </div>
        )}

        {/* Announcement */}
        {roundAnnouncement && (
          <div className="stage-announcement">{roundAnnouncement}</div>
        )}

        {/* Only show the CURRENT player's judgement — not both */}
        {turnPhase === 'between_turns' && round.validation_reason && (
          <div className="stage-judgement">
            <div className="stage-judgement__verdict">
              {round.validation_valid ? '✓ VALID' : '✗ INVALID'} — {round.validation_steps} steps → {round.points_awarded} pts
            </div>
            <div className="stage-judgement__reason">{round.validation_reason}</div>
          </div>
        )}

        {pendingRoundAdvance && round.second_validation_reason && (
          <div className="stage-judgement">
            <div className="stage-judgement__verdict">
              {round.second_validation_valid ? '✓ VALID' : '✗ INVALID'} — {round.second_validation_steps} steps → {round.second_points_awarded} pts
            </div>
            <div className="stage-judgement__reason">{round.second_validation_reason}</div>
          </div>
        )}

        {/* Evaluating spinner for current player only */}
        {lastSubmittedSentence && turnPhase === 'first_player' && !round.validation_reason && (
          <div className="stage-judgement">
            <div className="stage-judgement__reason" style={{ fontStyle: 'italic' }}>
              Evaluating: "{lastSubmittedSentence}"
            </div>
          </div>
        )}

        {lastSubmittedSentence && turnPhase === 'second_player' && !round.second_validation_reason && (
          <div className="stage-judgement">
            <div className="stage-judgement__reason" style={{ fontStyle: 'italic' }}>
              Evaluating: "{lastSubmittedSentence}"
            </div>
          </div>
        )}
      </div>

      <div className="stage-scene">
        {/* Left contestant */}
        <div className="stage-contestant stage-contestant--left">
          <div className="stage-contestant__score">{game.team_left_score}</div>
          <ImagePlaceholder
            src={leftHidden ? '/placeholders/desk-empty.png' : `/placeholders/stickman-${teamLeftSkin}-${(leftHolding || secondLeftHolding) ? 'holding' : 'idle'}.png`}
            alt={teamLeftName}
            label={leftHidden ? 'EMPTY DESK' : (leftHolding || secondLeftHolding) ? 'LEFT HOLDING' : 'LEFT IDLE'}
            width={180}
            height={360}
            className="stage-contestant__sprite"
          />
          <div className="stage-contestant__name">{teamLeftName}</div>
        </div>

        {/* Centre: table + remote */}
        <div className="stage-centre">
          <div className="stage-table-wrap">
            <ImagePlaceholder
              src={tableSrc}
              alt="Table"
              label="TABLE"
              width={420}
              height={210}
              className="stage-table"
            />
            {!remoteGrabbed && !teleporting && (
              <ImagePlaceholder
                src={remoteSrc}
                alt="Remote"
                label="REMOTE"
                width={90}
                height={90}
                className="stage-remote"
              />
            )}
            {teleporting && (
              <ImagePlaceholder
                src={`/placeholders/stickman-${teleporting === 'left' ? teamLeftSkin : teamRightSkin}-flying.png`}
                alt="Teleporting Player"
                label="BAM!"
                width={180}
                height={360}
                className={`teleport-clone ${teleporting === 'right' ? 'sprite--flipped' : ''}`}
              />
            )}
          </div>
        </div>

        {/* Right contestant */}
        <div className="stage-contestant stage-contestant--right">
          <div className="stage-contestant__score">{game.team_right_score}</div>
          <ImagePlaceholder
            src={rightHidden ? '/placeholders/desk-empty.png' : `/placeholders/stickman-${teamRightSkin}-${(rightHolding || secondRightHolding) ? 'holding' : 'idle'}.png`}
            alt={teamRightName}
            label={rightHidden ? 'EMPTY DESK' : (rightHolding || secondRightHolding) ? 'RIGHT HOLDING' : 'RIGHT IDLE'}
            width={180}
            height={360}
            className="stage-contestant__sprite sprite--flipped"
          />
          <div className="stage-contestant__name">{teamRightName}</div>
        </div>
      </div>

      <div className="stage-banner__round">
        Round {game.current_round_number}/{game.total_rounds}
        {turnPhase === 'second_player' && ' — Player 2'}
        {turnPhase === 'first_player' && ' — Player 1'}
      </div>

      <div className="stage-bottom">
        <button className="stage-bottom__end" onClick={onForceEnd}>End Game</button>
      </div>
    </div>
  )
}
