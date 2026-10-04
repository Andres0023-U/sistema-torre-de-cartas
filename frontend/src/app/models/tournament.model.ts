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