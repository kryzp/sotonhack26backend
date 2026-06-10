import ImagePlaceholder from './ImagePlaceholder'

const arrowLeftSrc = '/placeholders/arrow-left.png'
const arrowRightSrc = '/placeholders/arrow-right.png'
const btnStartGameSrc = '/placeholders/btn-start-game.png'

const tutorialSlides = [
  'Welcome to Stick It Together! Two teams compete to connect two random words with a chain of logic.',
  'A prompt with two words appears on screen. Either team can grab the remote from the table to buzz in first.',
  'Once you grab the remote, explain your connection chain. The AI judges how logical and tight your links are.',
  'Your score = connection quality divided by number of steps. Tight chains with fewer steps = big points!',
  'Ready? Hit Start to begin the first round!',
]

type Props = {
  currentSlide: number
  onPrev: () => void
  onNext: () => void
  onStart: () => void
}

export default function TutorialOverlay({ currentSlide, onPrev, onNext, onStart }: Props) {
  const total = tutorialSlides.length
  const isFirst = currentSlide === 0
  const isLast = currentSlide === total - 1

  return (
    <div className="tutorial-backdrop">
      <div className="tutorial-card">
        <p className="tutorial-counter">{currentSlide + 1} / {total}</p>

        <div className="tutorial-text">
          <p>{tutorialSlides[currentSlide]}</p>
        </div>

        <div className="tutorial-nav">
          <ImagePlaceholder
            src={arrowLeftSrc}
            alt="Previous"
            label="← PREV"
            width={64}
            height={64}
            className={`tutorial-arrow ${isFirst ? 'tutorial-arrow--hidden' : ''}`}
            onClick={isFirst ? undefined : onPrev}
          />

          {isLast ? (
            <ImagePlaceholder
              src={btnStartGameSrc}
              alt="Start Game"
              label="START"
              width={200}
              height={80}
              className="tutorial-start-btn"
              onClick={onStart}
            />
          ) : (
            <ImagePlaceholder
              src={arrowRightSrc}
              alt="Next"
              label="NEXT →"
              width={64}
              height={64}
              className="tutorial-arrow"
              onClick={onNext}
            />
          )}
        </div>
      </div>
    </div>
  )
}
