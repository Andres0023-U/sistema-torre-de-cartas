import { Routes } from '@angular/router';
import { Login } from './features/auth/login/login';
import { Home } from './features/home/home';
import { TournamentList } from './features/tournaments/tournament-list/tournament-list';
import { TournamentDetail } from './features/tournaments/tournament-detail/tournament-detail';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: '', component: Home, canActivate: [authGuard] },
  { path: 'tournaments', component: TournamentList, canActivate: [authGuard] },
  { path: 'tournaments/:id', component: TournamentDetail, canActivate: [authGuard] }
];