import ImagePlaceholder from './ImagePlaceholder'

const titleSrc = '/placeholders/title.png'
const btnStartSrc = '/placeholders/btn-start.png'
const btnExitSrc = '/placeholders/btn-exit.png'

type Props = {
  onStart: () => void
}

export default function MenuScreen({ onStart }: Props) {
  return (
    <div className="screen-menu">
      <ImagePlaceholder
        src={titleSrc}
        alt="Stick It Together"
        label="TITLE GRAPHIC"
        width={600}
        height={200}
      />
      <div className="menu-buttons">
        <ImagePlaceholder
          src={btnStartSrc}
          alt="Start Game"
          label="START BUTTON"
          width={200}
          height={80}
          onClick={onStart}
        />
      </div>
    </div>
  )
}
