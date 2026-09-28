export interface Round {
  id: number;
  number: number;
  name: string; // ej. 'Cuartos de final', 'Semifinal', 'Final'
  tournamentId: number;
}