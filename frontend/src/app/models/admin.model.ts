export interface PendingUser {
  userId: number;
  name: string;
  email: string;
}

export type AssignableRole = 'organizer' | 'player';

export interface AdminUser {
  userId: number;
  name: string;
  email: string;
  role: string;
  isActive: boolean;
}