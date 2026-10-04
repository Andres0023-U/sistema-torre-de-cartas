import { Routes } from '@angular/router';
import { Login } from './features/auth/login/login';
import { Home } from './features/home/home';
import { TournamentList } from './features/tournaments/tournament-list/tournament-list';
import { TournamentDetail } from './features/tournaments/tournament-detail/tournament-detail';
import { authGuard } from './core/guards/auth-guard';
import { DeckList } from './features/decks/deck-list/deck-list';
import { DeckDetail } from './features/decks/deck-detail/deck-detail';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: '', component: Home, canActivate: [authGuard] },
  { path: 'tournaments', component: TournamentList, canActivate: [authGuard] },
  { path: 'tournaments/:id', component: TournamentDetail, canActivate: [authGuard] },
  { path: 'decks', component: DeckList, canActivate: [authGuard] },
  { path: 'decks/:id', component: DeckDetail, canActivate: [authGuard] }
];