import { useState } from 'react'
import ImagePlaceholder from './ImagePlaceholder'
import type { Difficulty } from '../types'

type Props = {
  teamLeftName: string
  teamRightName: string
  onComplete: (leftSkin: string, rightSkin: string, leftName: string, rightName: string, rounds: number, difficulty: Difficulty) => void
}

const SKINS = ['blue', 'red', 'green', 'yellow']
const ROUND_OPTIONS = [1, 3, 5, 7, 9]
const DIFFICULTY_OPTIONS: { value: Difficulty; label: string; desc: string }[] = [
  { value: 'hard', label: 'Normal', desc: 'Be precise' },
  { value: 'brutal', label: 'Difficult', desc: 'No mercy' },
]

export default function SkinSelectionScreen({ teamLeftName: defaultLeft, teamRightName: defaultRight, onComplete }: Props) {
  const [leftSkin, setLeftSkin] = useState('blue')
  const [rightSkin, setRightSkin] = useState('red')
  const [leftName, setLeftName] = useState(defaultLeft)
  const [rightName, setRightName] = useState(defaultRight)
  const [rounds, setRounds] = useState(3)
  const [difficulty, setDifficulty] = useState<Difficulty>('medium')

  return (
    <div className="screen-selection">
      <h1 className="selection-title">Game Setup</h1>

      {/* Settings row */}
      <div className="settings-row">
        <div className="settings-group">
          <label className="settings-label">Rounds</label>
          <div className="settings-pills">
            {ROUND_OPTIONS.map(r => (
              <button
                key={r}
                className={`settings-pill ${rounds === r ? 'settings-pill--active' : ''}`}
                onClick={() => setRounds(r)}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        <div className="settings-group">
          <label className="settings-label">Difficulty</label>
          <div className="settings-pills">
            {DIFFICULTY_OPTIONS.map(d => (
              <button
                key={d.value}
                className={`settings-pill ${difficulty === d.value ? 'settings-pill--active' : ''}`}
                onClick={() => setDifficulty(d.value)}
                title={d.desc}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Player setup */}
      <div className="selection-wrapper">
        <div className="selection-player">
          <input
            className="selection-name-input"
            value={leftName}
            onChange={e => setLeftName(e.target.value)}
            placeholder="Team name..."
            maxLength={20}
          />
          <div className="selection-preview">
            <ImagePlaceholder
              src={`/placeholders/stickman-${leftSkin}-idle.png`}
              alt={`${leftSkin} skin`}
              label="SKIN"
              width={150}
              height={200}
              className="selection-sprite"
            />
          </div>
          <div className="selection-options">
            {SKINS.map(skin => (
              <button
                key={`left-${skin}`}
                className={`selection-btn ${leftSkin === skin ? 'selection-btn--active' : ''}`}
                style={{ backgroundColor: skin === 'yellow' ? '#f1c40f' : skin === 'red' ? '#e74c3c' : skin === 'blue' ? '#4a90d9' : '#5cb85c' }}
                onClick={() => setLeftSkin(skin)}
              />
            ))}
          </div>
        </div>

        <div className="selection-vs">VS</div>

        <div className="selection-player">
          <input
            className="selection-name-input"
            value={rightName}
            onChange={e => setRightName(e.target.value)}
            placeholder="Team name..."
            maxLength={20}
          />
          <div className="selection-preview">
            <ImagePlaceholder
              src={`/placeholders/stickman-${rightSkin}-idle.png`}
              alt={`${rightSkin} skin`}
              label="SKIN"
              width={150}
              height={200}
              className="selection-sprite selection-sprite--flipped"
            />
          </div>
          <div className="selection-options">
            {SKINS.map(skin => (
              <button
                key={`right-${skin}`}
                className={`selection-btn ${rightSkin === skin ? 'selection-btn--active' : ''}`}
                style={{ backgroundColor: skin === 'yellow' ? '#f1c40f' : skin === 'red' ? '#e74c3c' : skin === 'blue' ? '#4a90d9' : '#5cb85c' }}
                onClick={() => setRightSkin(skin)}
              />
            ))}
          </div>
        </div>
      </div>

      <button
        className="action-btn"
        onClick={() => onComplete(leftSkin, rightSkin, leftName || defaultLeft, rightName || defaultRight, rounds, difficulty)}
      >
        LET'S GO!
      </button>
    </div>
  )
}
