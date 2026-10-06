import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { TournamentService } from '../../../core/services/tournament';
import { PlayerService } from '../../../core/services/player';
import { Tournament, Round } from '../../../models/tournament.model';
import { PlayerWithUser } from '../../../models/player.model';

@Component({
  selector: 'app-tournament-detail',
  imports: [RouterLink],
  templateUrl: './tournament-detail.html',
  styleUrl: './tournament-detail.css'
})
export class TournamentDetail implements OnInit {
  tournament: Tournament | null = null;
  allPlayers: PlayerWithUser[] = [];
  registeredIds: number[] = [];
  rounds: Round[] = [];
  errorMessage = '';
  successMessage = '';

  tournamentId!: number;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private tournamentService: TournamentService,
    private playerService: PlayerService,
    private cdr: ChangeDetectorRef
  ) {}

  get availablePlayers(): PlayerWithUser[] {
    return this.allPlayers.filter(p => !this.registeredIds.includes(p.playerId));
  }

  ngOnInit(): void {
    this.tournamentId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadAll();
  }

  loadAll(): void {
    this.tournamentService.getTournaments().subscribe({
      next: (list) => {
        this.tournament = list.find(t => t.tournamentId === this.tournamentId) ?? null;
        this.cdr.markForCheck();

        if (this.tournament && this.tournament.status !== 'pending') {
          this.tournamentService.getRounds(this.tournamentId).subscribe({
            next: (rounds) => {
              this.rounds = rounds;
              this.cdr.markForCheck();
            }
          });
        }
      }
    });

    this.playerService.getPlayers().subscribe({
      next: (players) => {
        this.allPlayers = players;
        this.cdr.markForCheck();
      }
    });

    this.tournamentService.getRegisteredPlayers(this.tournamentId).subscribe({
      next: (ids) => {
        this.registeredIds = ids;
        this.cdr.markForCheck();
      }
    });
  }

  onRegister(playerId: number): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.tournamentService.registerPlayer(this.tournamentId, playerId).subscribe({
      next: () => {
        this.successMessage = 'Jugador inscrito';
        this.loadAll();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo inscribir al jugador';
        this.cdr.markForCheck();
      }
    });
  }

  onStart(): void {
    this.errorMessage = '';
    this.tournamentService.startTournament(this.tournamentId).subscribe({
      next: () => {
        this.successMessage = 'Torneo iniciado';
        this.loadAll();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo iniciar el torneo';
        this.cdr.markForCheck();
      }
    });
  }
}