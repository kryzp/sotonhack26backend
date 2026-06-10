import { useEffect, useMemo, useRef, useState } from 'react'

import { api } from './api'
import MenuScreen from './components/MenuScreen'
import TutorialOverlay from './components/TutorialOverlay'
import SkinSelectionScreen from './components/SkinSelectionScreen'
import GameStage from './components/GameStage'
import ResultsScreen from './components/ResultsScreen'
import { timerStartSeconds } from './gameData'
import type { Difficulty, GameResponse, PlayerScore, RoundResponse, Screen } from './types'
import buzzerSrc from './assets/buzzer.mp3'

const backgroundSrc = '/placeholders/background.png'

declare global {
  interface Window {
    onSpeechResult: ((transcript: string) => void) | null
    onPartialSpeechResult: ((transcript: string) => void) | null
    onSpeechStateChange: ((state: string) => void) | null
    onSpeechError: ((error: string) => void) | null
  }
}

declare global {
  interface Window {
    onSpeechResult: ((transcript: string) => void) | null
    onPartialSpeechResult: ((transcript: string) => void) | null
    onSpeechStateChange: ((state: string) => void) | null
    onSpeechError: ((error: string) => void) | null
    AndroidBridge?: {
      startListening: () => void
      stopListening: () => void
      isListening: () => boolean
      showToast: (message: string) => void
    }
  }
}

export type TurnPhase = 'presenting' | 'waiting_buzzer' | 'buzzer_open' | 'first_player' | 'between_turns' | 'second_player'

function App() {
  const [screen, setScreen] = useState<Screen>('menu')

  const [game, setGame] = useState<GameResponse | null>(null)
  const [currentRound, setCurrentRound] = useState<RoundResponse | null>(null)

  const [secondsLeft, setSecondsLeft] = useState(timerStartSeconds)
  const [liveSentence, setLiveSentence] = useState('')
  const [lastSubmittedSentence, setLastSubmittedSentence] = useState('')
  const [roundAnnouncement, setRoundAnnouncement] = useState('')
  const [pendingRoundAdvance, setPendingRoundAdvance] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  // Two-turn phase tracking
  const [turnPhase, setTurnPhase] = useState<TurnPhase>('waiting_buzzer')
  const [firstPlayerAnswer, setFirstPlayerAnswer] = useState('')

  // Tutorial state
  const [tutorialSlide, setTutorialSlide] = useState(0)

  // Player names
  const [teamLeftName, setTeamLeftName] = useState('Team 1')
  const [teamRightName, setTeamRightName] = useState('Team 2')

  // Game settings
  const [gameRounds, setGameRounds] = useState(3)
  const [gameDifficulty, setGameDifficulty] = useState<Difficulty>('medium')

  // Derived state for the UI
  const isFirstPlayerAnswering = turnPhase === 'first_player' && (currentRound?.status === 'answering' || currentRound?.status === 'side_selected')
  const isSecondPlayerAnswering = turnPhase === 'second_player' && (currentRound?.status === 'second_answering' || currentRound?.status === 'first_resolved')
  const isAnswering = isFirstPlayerAnswering || isSecondPlayerAnswering
  const isSpeaking = screen === 'game' && isAnswering && !pendingRoundAdvance

  const playerScores: PlayerScore[] = useMemo(() => {
    if (!game) return [
      { id: 'left', name: teamLeftName, title: '', color: '#54e0c7', score: 0 },
      { id: 'right', name: teamRightName, title: '', color: '#ff9f59', score: 0 },
    ]
    return [
      { id: 'left', name: game.team_left_name, title: '', color: '#54e0c7', score: game.team_left_score },
      { id: 'right', name: game.team_right_name, title: '', color: '#ff9f59', score: game.team_right_score },
    ].sort((a, b) => a.score - b.score) // Lowest score wins
  }, [game, teamLeftName, teamRightName])

  const winningPlayer = playerScores[0]


  // Timer countdown — runs during both first and second player turns
  useEffect(() => {
    if (screen !== 'game' || pendingRoundAdvance || !isAnswering) return

    const intervalId = window.setInterval(() => {
      setSecondsLeft((currentSeconds) => {
        if (currentSeconds <= 0) return 0
        return currentSeconds - 1
      })
    }, 1000)

    return () => window.clearInterval(intervalId)
  }, [screen, isAnswering, pendingRoundAdvance])

  // Timer run out
  useEffect(() => {
    if (secondsLeft === 0 && isAnswering && !pendingRoundAdvance && !isProcessing) {
      if (turnPhase === 'first_player') {
        handleFirstPlayerSubmit()
      } else if (turnPhase === 'second_player') {
        handleSecondPlayerSubmit()
      }
    }
  }, [secondsLeft, isAnswering, pendingRoundAdvance, isProcessing, turnPhase])

  // Automatically advance round logic (only after second player is done)
  useEffect(() => {
    if (!pendingRoundAdvance) return

    const timeoutId = window.setTimeout(() => {
      moveToNextRound()
    }, 4000)

    return () => window.clearTimeout(timeoutId)
  }, [pendingRoundAdvance])

  // Buzzer random delay — play buzzer.mp3 after 2-8s then open buzz buttons
  const buzzerTimeoutRef = useRef<number | null>(null)
  useEffect(() => {
    if (turnPhase !== 'waiting_buzzer' || screen !== 'game') return

    const delay = 2000 + Math.random() * 6000 // 2-8 seconds
    buzzerTimeoutRef.current = window.setTimeout(() => {
      const audio = new Audio(buzzerSrc)
      audio.play().catch(() => { })
      setTurnPhase('buzzer_open')
    }, delay)

    return () => {
      if (buzzerTimeoutRef.current) window.clearTimeout(buzzerTimeoutRef.current)
    }
  }, [turnPhase, screen])

  // Speech thing
  useEffect(() => {
    window.onPartialSpeechResult = (transcript: string) => {
      setLiveSentence(transcript)
    }
    window.onSpeechResult = (transcript: string) => {
      setLiveSentence(transcript)
    }
    window.onSpeechStateChange = (state: string) => {
      console.log(`[Speech] State changed: ${state}`)
    }
    window.onSpeechError = (error: string) => {
      console.error(`[Speech] Error: ${error}`)
    }
    return () => {
      window.onPartialSpeechResult = null
      window.onSpeechResult = null
    }
  }, [])

  useEffect(() => {
    if (turnPhase === 'first_player' || turnPhase === 'second_player') {
      if (window.AndroidBridge?.startListening) {
        window.AndroidBridge.startListening()
      }
    } else {
      if (window.AndroidBridge?.stopListening) {
        window.AndroidBridge.stopListening()
      }
    }
  }, [turnPhase])

  // ── TTS Commentary ──

  const currentAudioRef = useRef<HTMLAudioElement | null>(null)

  async function playCommentary(gameId: number, event: string, context: Record<string, unknown> = {}): Promise<void> {
    const { audioUrl, text } = await api.generateCommentary(gameId, event, context)
    if (text) console.log(`[Commentary] ${event}: ${text}`)
    if (!audioUrl) return

    // Stop any currently playing commentary
    if (currentAudioRef.current) {
      currentAudioRef.current.pause()
      currentAudioRef.current.onended = null
      if (currentAudioRef.current.src) URL.revokeObjectURL(currentAudioRef.current.src)
    }

    const audio = new Audio(audioUrl)
    currentAudioRef.current = audio

    return new Promise<void>((resolve) => {
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        if (currentAudioRef.current === audio) currentAudioRef.current = null
        resolve()
      }
      audio.onerror = () => {
        URL.revokeObjectURL(audioUrl)
        if (currentAudioRef.current === audio) currentAudioRef.current = null
        resolve()
      }
      audio.play().catch(() => resolve())
    })
  }

  // ── Navigation handlers ──

  function handleMenuStart() {
    setTutorialSlide(0)
    setScreen('tutorial')
  }

  function handleTutorialComplete() {
    setScreen('skinSelection')
  }

  // Skin state
  const [teamLeftSkin, setTeamLeftSkin] = useState('red')
  const [teamRightSkin, setTeamRightSkin] = useState('blue')

  async function handleSkinSelectionComplete(leftSkin: string, rightSkin: string, leftName: string, rightName: string, rounds: number, difficulty: Difficulty) {
    setTeamLeftSkin(leftSkin)
    setTeamRightSkin(rightSkin)
    setTeamLeftName(leftName)
    setTeamRightName(rightName)
    setGameRounds(rounds)
    setGameDifficulty(difficulty)
    try {
      setIsProcessing(true)
      const newGame = await api.createGame(rounds, 'team', difficulty, leftName, rightName)
      await api.startGame(newGame.id!)

      await api.nextRound(newGame.id!)
      const buzzedRound = await api.openBuzz(newGame.id!)

      setGame(newGame)
      setCurrentRound(buzzedRound)
      setScreen('game')
      resetTurnState()
      setTurnPhase('presenting')

      // TTS: announce game start
      await playCommentary(newGame.id!, 'game_started', {
        team_left: leftName,
        team_right: rightName,
        round_number: 1,
        total_rounds: newGame.total_rounds,
      })

      // TTS: present the words clearly
      await playCommentary(newGame.id!, 'words_presented', {
        word_one: buzzedRound.word_one,
        word_two: buzzedRound.word_two,
      })

      // Presenter done — now start buzzer countdown
      setTurnPhase('waiting_buzzer')
    } catch (err: any) {
      console.error(err)
      alert(`Failed to start game: ${err.message}`)
    } finally {
      setIsProcessing(false)
    }
  }

  function resetTurnState() {
    setSecondsLeft(timerStartSeconds)
    setLiveSentence('')
    setLastSubmittedSentence('')
    setRoundAnnouncement('')
    setPendingRoundAdvance(false)
    setFirstPlayerAnswer('')
  }

  async function handleBuzz(side: 'left' | 'right') {
    if (!game || !currentRound || isProcessing) return
    try {
      setIsProcessing(true)
      const player = side === 'left' ? 'left' : 'right'
      await api.buzz(game.id!, player)
      const updatedRound = await api.selectSide(game.id!, side)
      setCurrentRound(updatedRound)
      setTurnPhase('first_player')
      setSecondsLeft(timerStartSeconds)
      const buzzerName = side === 'left' ? teamLeftName : teamRightName
      setRoundAnnouncement(`${buzzerName} goes first!`)

      // TTS: announce who buzzed
      await playCommentary(game.id!, 'buzz_locked', {
        player_name: buzzerName,
        side,
        word_one: currentRound.word_one,
        word_two: currentRound.word_two,
      })
    } catch (err) {
      console.error(err)
      alert("Buzzer was locked or an error occurred")
    } finally {
      setIsProcessing(false)
    }
  }

  async function handleFirstPlayerSubmit() {
    if (!game || !currentRound || isProcessing || pendingRoundAdvance) return
    try {
      setIsProcessing(true)
      const submittedSentence = liveSentence.trim() || `${currentRound.word_one} connects to ${currentRound.word_two}`
      setLastSubmittedSentence(submittedSentence)
      setFirstPlayerAnswer(submittedSentence)

      // Submit transcript then answer
      await api.submitTranscript(game.id!, submittedSentence)
      await api.submitFinalAnswer(game.id!, submittedSentence)

      // Validate with Gemini
      setRoundAnnouncement("Validating with Gemini...")

      await playCommentary(game.id!, 'validation_started', {})

      const validatedRound = await api.validateRound(game.id!)
      setCurrentRound(validatedRound)

      const updatedGame = await api.getGame(game.id!)
      setGame(updatedGame)

      if (validatedRound.validation_valid) {
        setRoundAnnouncement(`${validatedRound.validation_steps} steps → ${validatedRound.points_awarded} pts`)
      } else {
        setRoundAnnouncement(`Invalid! ${validatedRound.validation_reason} → ${validatedRound.points_awarded} penalty pts`)
      }

      await playCommentary(game.id!, 'validation_complete', {
        valid: validatedRound.validation_valid,
        steps: validatedRound.validation_steps,
        score: validatedRound.validation_score,
        reason: validatedRound.validation_reason,
        answer: submittedSentence,
        word_one: currentRound.word_one,
        word_two: currentRound.word_two,
        selected_side: validatedRound.selected_side,
        team_left_score: updatedGame.team_left_score,
        team_right_score: updatedGame.team_right_score,
      })

      // Transition to second player after a brief pause
      setTurnPhase('between_turns')
      setTimeout(() => {
        startSecondPlayerTurn(validatedRound)
      }, 3000)
    } catch (err) {
      console.error(err)
      alert("Failed to validate answer")
      setRoundAnnouncement("Error validating connection.")
    } finally {
      setIsProcessing(false)
    }
  }

  function startSecondPlayerTurn(round: RoundResponse) {
    const secondSide = round.second_selected_side
    const secondName = secondSide === 'left' ? teamLeftName : teamRightName
    setTurnPhase('second_player')
    setSecondsLeft(timerStartSeconds)
    setLiveSentence('')
    setLastSubmittedSentence('')
    setRoundAnnouncement(`${secondName}'s turn! Don't reuse the same steps!`)
  }

  async function handleSecondPlayerSubmit() {
    if (!game || !currentRound || isProcessing || pendingRoundAdvance) return
    try {
      setIsProcessing(true)
      const submittedSentence = liveSentence.trim() || `${currentRound.word_one} connects to ${currentRound.word_two}`
      setLastSubmittedSentence(submittedSentence)

      // Submit second player transcript + answer
      await api.submitSecondTranscript(game.id!, submittedSentence)
      await api.submitSecondAnswer(game.id!, submittedSentence)

      // Validate with Gemini (includes overlap detection)
      setRoundAnnouncement("Validating with Gemini...")

      await playCommentary(game.id!, 'validation_started', {})

      const validatedRound = await api.validateSecondRound(game.id!)
      setCurrentRound(validatedRound)

      const updatedGame = await api.getGame(game.id!)
      setGame(updatedGame)

      if (validatedRound.second_validation_valid) {
        setRoundAnnouncement(`${validatedRound.second_validation_steps} steps → ${validatedRound.second_points_awarded} pts`)
      } else {
        setRoundAnnouncement(`Invalid! ${validatedRound.second_validation_reason} → ${validatedRound.second_points_awarded} penalty pts`)
      }

      await playCommentary(game.id!, 'validation_complete', {
        valid: validatedRound.second_validation_valid,
        steps: validatedRound.second_validation_steps,
        score: validatedRound.second_validation_score,
        reason: validatedRound.second_validation_reason,
        answer: submittedSentence,
        word_one: currentRound.word_one,
        word_two: currentRound.word_two,
        selected_side: validatedRound.second_selected_side,
        team_left_score: updatedGame.team_left_score,
        team_right_score: updatedGame.team_right_score,
      })

      setPendingRoundAdvance(true)
    } catch (err) {
      console.error(err)
      alert("Failed to validate answer")
      setRoundAnnouncement("Error validating connection.")
      setPendingRoundAdvance(true)
    } finally {
      setIsProcessing(false)
    }
  }

  // Unified submit handler — dispatches based on turn phase
  function handleSubmit() {
    if (turnPhase === 'first_player') {
      handleFirstPlayerSubmit()
    } else if (turnPhase === 'second_player') {
      handleSecondPlayerSubmit()
    }
  }

  async function moveToNextRound() {
    if (!game) return
    try {
      setIsProcessing(true)

      // Refresh game to get latest scores/status
      const latestGame = await api.getGame(game.id!)
      setGame(latestGame)

      if (latestGame.current_round_number >= latestGame.total_rounds) {
        // TTS: announce game over
        await playCommentary(latestGame.id!, 'game_finished', {
          team_left: teamLeftName,
          team_right: teamRightName,
          team_left_score: latestGame.team_left_score,
          team_right_score: latestGame.team_right_score,
          winner: latestGame.winner,
        })
        setScreen('results')
        return
      }

      await api.nextRound(latestGame.id!)
      const buzzedRound = await api.openBuzz(latestGame.id!)

      const updatedGame = await api.getGame(latestGame.id!)

      setGame(updatedGame)
      setCurrentRound(buzzedRound)
      resetTurnState()
      setTurnPhase('presenting')

      // TTS: announce new round
      await playCommentary(updatedGame.id!, 'round_started', {
        round_number: updatedGame.current_round_number,
        total_rounds: updatedGame.total_rounds,
        team_left: teamLeftName,
        team_right: teamRightName,
        team_left_score: updatedGame.team_left_score,
        team_right_score: updatedGame.team_right_score,
      })

      // TTS: present the words clearly
      await playCommentary(updatedGame.id!, 'words_presented', {
        word_one: buzzedRound.word_one,
        word_two: buzzedRound.word_two,
      })

      // Presenter done — now start buzzer countdown
      setTurnPhase('waiting_buzzer')
    } catch (err) {
      console.error(err)
      alert("Failed to move to next round")
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <>
      {/* Background image (behind everything) */}
      <div className="app-bg">
        <img src={backgroundSrc} alt="" />
      </div>

      <div className="app-wrap">
        {screen === 'menu' && (
          <MenuScreen onStart={handleMenuStart} />
        )}

        {screen === 'tutorial' && (
          <TutorialOverlay
            currentSlide={tutorialSlide}
            onPrev={() => setTutorialSlide(s => Math.max(0, s - 1))}
            onNext={() => setTutorialSlide(s => s + 1)}
            onStart={handleTutorialComplete}
          />
        )}

        {screen === 'skinSelection' && (
          <SkinSelectionScreen
            teamLeftName={teamLeftName}
            teamRightName={teamRightName}
            onComplete={handleSkinSelectionComplete}
          />
        )}

        {screen === 'game' && game && currentRound && (
          <GameStage
            game={game}
            round={currentRound}
            teamLeftName={teamLeftName}
            teamRightName={teamRightName}
            teamLeftSkin={teamLeftSkin}
            teamRightSkin={teamRightSkin}
            secondsLeft={secondsLeft}
            maxSeconds={timerStartSeconds}
            liveSentence={liveSentence}
            roundAnnouncement={roundAnnouncement}
            lastSubmittedSentence={lastSubmittedSentence}
            isSpeaking={isSpeaking}
            isAnswering={isAnswering}
            pendingRoundAdvance={pendingRoundAdvance}
            isProcessing={isProcessing}
            turnPhase={turnPhase}
            firstPlayerAnswer={firstPlayerAnswer}
            onBuzz={handleBuzz}
            onSubmit={handleSubmit}
            onLiveSentenceChange={setLiveSentence}
            onForceEnd={() => {
              if (currentAudioRef.current) {
                currentAudioRef.current.pause()
                if (currentAudioRef.current.src) URL.revokeObjectURL(currentAudioRef.current.src)
                currentAudioRef.current = null
              }
              setScreen('results')
              setGame(null)
              setCurrentRound(null)
            }}
          />
        )}

        {screen === 'results' && (
          <ResultsScreen
            playerScores={playerScores}
            winnerName={winningPlayer.name}
            winnerTitle={winningPlayer.title}
            isTie={game?.winner === 'tie'}
            winnerScore={winningPlayer.score}
            onPlayAgain={() => setScreen('skinSelection')}
          />
        )}
      </div>
    </>
  )
}

export default App
