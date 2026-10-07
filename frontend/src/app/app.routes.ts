import { Routes } from '@angular/router';
import { Login } from './features/auth/login/login';
import { Home } from './features/home/home';
import { TournamentList } from './features/tournaments/tournament-list/tournament-list';
import { TournamentDetail } from './features/tournaments/tournament-detail/tournament-detail';
import { authGuard } from './core/guards/auth-guard';
import { adminGuard } from './core/guards/admin-guard';
import { DeckList } from './features/decks/deck-list/deck-list';
import { DeckDetail } from './features/decks/deck-detail/deck-detail';
import { RoundDetail } from './features/tournaments/round-detail/round-detail';
import { Register } from './features/auth/register/register';
import { AdminPanel } from './features/admin/admin-panel/admin-panel';
import { playerGuard } from './core/guards/player-guard';
import { Ranking } from './features/ranking/ranking';
import { Stats } from './features/stats/stats';
import { Account } from './features/account/account';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: '', component: Home, canActivate: [authGuard] },
  { path: 'tournaments', component: TournamentList, canActivate: [authGuard] },
  { path: 'tournaments/:id', component: TournamentDetail, canActivate: [authGuard] },
  { path: 'tournaments/:id/rounds/:roundId', component: RoundDetail, canActivate: [authGuard] },
  { path: 'decks', component: DeckList, canActivate: [authGuard] },
  { path: 'decks/:id', component: DeckDetail, canActivate: [authGuard] },
  { path: 'admin', component: AdminPanel, canActivate: [adminGuard] },
  { path: 'decks', component: DeckList, canActivate: [authGuard, playerGuard] },
  { path: 'decks/:id', component: DeckDetail, canActivate: [authGuard, playerGuard] },
  { path: 'ranking', component: Ranking, canActivate: [authGuard] },
  { path: 'stats', component: Stats, canActivate: [authGuard] },
  { path: 'account', component: Account, canActivate: [authGuard] }
];