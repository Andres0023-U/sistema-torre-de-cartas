export interface Tournament {
  id: number;
  name: string;
  date: string;
  format: 'single_elimination';
  numParticipants: 4 | 8 | 16 | 32;
  status: 'pending' | 'in_progress' | 'finished';
  organizerId: number;
}