import { Routes } from '@angular/router';
import { Login } from './features/auth/login/login';
import { Home } from './features/home/home';
import { authGuard } from './core/guards/auth-guard';
import { TournamentList } from './features/tournaments/tournament-list/tournament-list';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: '', component: Home, canActivate: [authGuard] },
  { path: 'tournaments', component: TournamentList, canActivate: [authGuard] }
];