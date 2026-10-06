export interface PendingUser {
  userId: number;
  name: string;
  email: string;
}

export type AssignableRole = 'organizer' | 'player';