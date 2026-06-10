import type { PlayerScore } from '../types'

type Props = {
  playerScores: PlayerScore[]
  winnerName: string
  winnerTitle: string
  isTie: boolean
  winnerScore: number
  onPlayAgain: () => void
}

export default function ResultsScreen({
  playerScores,
  winnerName,
  winnerTitle,
  isTie,
  winnerScore,
  onPlayAgain,
}: Props) {
  return (
    <div className="screen-results">
      <div className="results-card">
        <p className="results-card__eyebrow">Winner</p>
        <h2 className="results-card__winner">{winnerName}</h2>
        <p className="results-card__detail">{winnerTitle}</p>
        <p className="results-card__detail">
          {isTie ? 'Tie Game' : `${winnerScore} steps total (lower is better)`}
        </p>
      </div>

      <div className="results-scores">
        {playerScores.map((p, i) => (
          <div
            key={p.id}
            className={`results-scores__row ${i === 0 ? 'results-scores__row--winner' : ''}`}
          >
            <span className="results-scores__name">
              #{i + 1} {p.name}
            </span>
            <span className="results-scores__score">{p.score}</span>
          </div>
        ))}
      </div>

      <button className="action-btn" onClick={onPlayAgain}>
        Play Again
      </button>
    </div>
  )
}
