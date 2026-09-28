export interface Result {
  id: number;
  matchId: number;
  winnerDeckId: number | null;
  endPhase: 'normal' | 'overtime' | null;
  lifePlayer1: number | null;
  lifePlayer2: number | null;
  pointsPlayer1: number | null;
  pointsPlayer2: number | null;
  dateTime: string | null;
}