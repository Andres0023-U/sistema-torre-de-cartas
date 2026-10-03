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