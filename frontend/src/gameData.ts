import type { Player, PlayerScore, RoundData } from './types'

export const players: Player[] = [
  {
    id: 'maya',
    name: 'Maya',
    title: 'Analogy Specialist',
    color: '#54e0c7',
  },
  {
    id: 'leo',
    name: 'Leo',
    title: 'Wildcard Connector',
    color: '#ff9f59',
  },
  {
    id: 'zara',
    name: 'Zara',
    title: 'High-Risk Improviser',
    color: '#a78bfa',
  },
  {
    id: 'noah',
    name: 'Noah',
    title: 'Crowd Favorite',
    color: '#f871b5',
  },
]

export const rounds: RoundData[] = [
  {
    id: 1,
    prompt: { left: 'Toaster', right: 'Ancient Rome' },
    transcript: [
      'Toasters make bread a star, bread comes from ovens, and communal ovens were a real social fixture in Roman cities.',
      'So the jump is weird, but it feels believable: breakfast tech to public baking culture to Ancient Rome.',
    ],
    judgement:
      'Strong crowd-pleaser. The chain stayed clear, escalated naturally, and landed on a recognisable Roman detail.',
    awardedPlayerId: 'maya',
    awardedPoints: 9,
    cue: 'Logical stretch with a satisfying finish.',
  },
  {
    id: 2,
    prompt: { left: 'Skateboard', right: 'Volcano' },
    transcript: [
      'A skateboard means wheels, wheels mean motion and friction, friction means heat, and heat takes us straight to molten rock.',
      'It is reckless, but it has momentum all the way through.',
    ],
    judgement:
      'Messy in the middle, fun in delivery. The audience can track it, which matters more than perfect academic rigor in a party round.',
    awardedPlayerId: 'leo',
    awardedPoints: 7,
    cue: 'Chaotic energy, still coherent enough to score.',
  },
  {
    id: 3,
    prompt: { left: 'Bubble Wrap', right: 'Shakespeare' },
    transcript: [
      'Bubble wrap pops, popping gets a reaction, theatre lives on reaction, and Shakespeare is the ultimate reference point for dramatic performance.',
      'The bridge is social experience rather than object similarity, which makes it land as a clever detour.',
    ],
    judgement:
      'Stylish answer. Not the shortest route, but the audience payoff is excellent and the logic remains visible.',
    awardedPlayerId: 'zara',
    awardedPoints: 8,
    cue: 'Creative detour with strong stage-show flavor.',
  },
  {
    id: 4,
    prompt: { left: 'Espresso', right: 'Moon Landing' },
    transcript: [
      'Espresso wakes people up, wakefulness powers late-night engineering, engineering powers rockets, and rockets get us to the moon.',
      'It feels like an overconfident pitch deck in the best possible way.',
    ],
    judgement:
      'Fast, sharp, and very demo-friendly. The chain is broad, but it is easy to follow from across the room.',
    awardedPlayerId: 'noah',
    awardedPoints: 10,
    cue: 'Simple line, big finish.',
  },
]

export const timerStartSeconds = 30

export function calculateScores(roundCount: number): PlayerScore[] {
  return players
    .map((player) => {
      const score = rounds
        .slice(0, roundCount)
        .filter((round) => round.awardedPlayerId === player.id)
        .reduce((total, round) => total + round.awardedPoints, 0)

      return {
        ...player,
        score,
      }
    })
    .sort((first, second) => second.score - first.score)
}