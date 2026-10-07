import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { StatusLabelPipe } from '../../../shared/pipes/status-label';
import { TournamentService } from '../../../core/services/tournament';
import { PlayerService } from '../../../core/services/player';
import { Tournament, Round, TournamentRanking } from '../../../models/tournament.model';
import { PlayerWithUser, TournamentPlayer } from '../../../models/player.model';

@Component({
  selector: 'app-tournament-detail',
  imports: [RouterLink, StatusLabelPipe],
  templateUrl: './tournament-detail.html',
  styleUrl: './tournament-detail.css',
})
export class TournamentDetail implements OnInit {
  tournament: Tournament | null = null;
  allPlayers: PlayerWithUser[] = [];
  registeredPlayers: TournamentPlayer[] = [];
  rounds: Round[] = [];
  ranking: TournamentRanking | null = null;
  loading = true;
  errorMessage = '';
  successMessage = '';

  tournamentId!: number;

  constructor(
    private route: ActivatedRoute,
    private tournamentService: TournamentService,
    private playerService: PlayerService,
    private cdr: ChangeDetectorRef
  ) {}

  get isOrganizer(): boolean {
    const role = localStorage.getItem('role');
    return role === 'organizer' || role === 'admin';
  }

  get registeredIds(): number[] {
    return this.registeredPlayers.map(p => p.playerId);
  }

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
        this.loading = false;
        this.cdr.markForCheck();

        if (!this.tournament) return;

        this.tournamentService.getTournamentPlayers(this.tournamentId).subscribe({
          next: (players) => {
            this.registeredPlayers = players;
            this.cdr.markForCheck();
          }
        });

        if (this.tournament.status !== 'pending') {
          this.tournamentService.getRounds(this.tournamentId).subscribe({
            next: (rounds) => {
              this.rounds = rounds;
              this.cdr.markForCheck();
            }
          });

          this.tournamentService.getRanking(this.tournamentId).subscribe({
            next: (ranking) => {
              this.ranking = ranking;
              this.cdr.markForCheck();
            }
          });
        } else if (this.isOrganizer) {
          this.playerService.getPlayers().subscribe({
            next: (players) => {
              this.allPlayers = players;
              this.cdr.markForCheck();
            }
          });
        }
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.detail || 'No se pudo cargar el torneo';
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
    this.successMessage = '';
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