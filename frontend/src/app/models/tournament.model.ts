export interface Tournament {
  tournamentId: number;
  name: string;
  date: string;
  format: string;
  numPlayers: number;
  status: 'pending' | 'in_progress' | 'finished';
  organizerId: number;
}

export interface TournamentCreate {
  name: string;
  date: string;
  format: string;
  numPlayers: number;
}

export interface Registration {
  tournamentRegistrationId: number;
  tournamentId: number;
  playerId: number;
}

export interface Round {
  roundId: number;
  tournamentId: number;
  number: number;
  name: string;
  status: string;
}

export interface StartTournamentResponse {
  tournamentId: number;
  status: string;
  roundId: number;
}

export interface Match {
  matchId: number;
  roundId: number;
  deck1Id: number;
  deck2Id: number;
}

export interface Result {
  resultId: number;
  matchId: number;
  winnerId: number;
  endPhase: string;
  player1FinalLife: number;
  player2FinalLife: number;
  player1Points: number;
  player2Points: number;
  date: string;
}

export interface ResultCreate {
  winnerId: number;
  endPhase: string;
  player1FinalLife: number;
  player2FinalLife: number;
}

export interface NextRoundResponse {
  status: string;
  roundId?: number;
  championDeckId?: number;
  championPlayerId?: number;
}