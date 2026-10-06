import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatchService } from '../../../core/services/match';
import { TournamentService } from '../../../core/services/tournament';
import { Match, Result, Round } from '../../../models/tournament.model';
import { PlayerService } from '../../../core/services/player';
import { DeckService } from '../../../core/services/deck';
import { PlayerWithUser } from '../../../models/player.model';

@Component({
  selector: 'app-round-detail',
  imports: [FormsModule],
  templateUrl: './round-detail.html',
  styleUrl: './round-detail.css'
})
export class RoundDetail implements OnInit {
  matches: Match[] = [];
  results: Record<number, Result> = {};
  forms: Record<number, any> = {};
  round: Round | null = null;
  errorMessage = '';
  successMessage = '';
  playerNames: Record<number, string> = {}; 
  private allPlayers: PlayerWithUser[] = [];

  tournamentId!: number;
  roundId!: number;

  constructor(
  private route: ActivatedRoute,
  private router: Router,
  private matchService: MatchService,
  private tournamentService: TournamentService,
  private deckService: DeckService,
  private playerService: PlayerService,
  private cdr: ChangeDetectorRef

  ) {}

  get allResultsIn(): boolean {
    return this.matches.length > 0 && this.matches.every(m => this.results[m.matchId]);
  }

  get isLastRoundPossible(): boolean {
    return this.matches.length === 1;
  }

  ngOnInit(): void {
    this.playerService.getPlayers().subscribe({
      next: (players) => this.allPlayers = players
    });

    this.route.paramMap.subscribe(params => {
      this.tournamentId = Number(params.get('id'));
      this.roundId = Number(params.get('roundId'));
      this.matches = [];
      this.results = {};
      this.forms = {};
      this.round = null;
      this.load();
    });
  }

  load(): void {
    this.tournamentService.getRounds(this.tournamentId).subscribe({
      next: (rounds) => {
        this.round = rounds.find(r => r.roundId === this.roundId) ?? null;
        this.cdr.markForCheck();
      }
    });

    this.matchService.getMatchesByRound(this.roundId).subscribe({
      next: (matches) => {
        this.matches = matches;

        matches.forEach(m => {
          this.loadDeckOwner(m.deck1Id);
          this.loadDeckOwner(m.deck2Id);
        });

        matches.forEach(m => {
          if (!this.forms[m.matchId]) {
            this.forms[m.matchId] = {
              winnerId: m.deck1Id,
              endPhase: 'normal',
              player1FinalLife: 0,
              player2FinalLife: 0
            };
          }
          this.matchService.getResult(m.matchId).subscribe({
            next: (result) => {
              if (result) {
                this.results[m.matchId] = result;
                this.cdr.markForCheck();
              }
            },
            error: () => {} // sin resultado todavía, 404 esperado
          });
        });
        this.cdr.markForCheck();
      }
    });
  }

  getResult(matchId: number): Result | null {
    return this.results[matchId] ?? null;
  }

  onGenerate(): void {
    this.errorMessage = '';
    this.matchService.generateMatches(this.roundId).subscribe({
      next: () => {
        this.successMessage = 'Emparejamientos generados';
        this.load();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo generar';
        this.cdr.markForCheck();
      }
    });
  }

  onSubmitResult(matchId: number): void {
    this.errorMessage = '';
    const form = this.forms[matchId];
    this.matchService.createResult(matchId, {
      winnerId: Number(form.winnerId),
      endPhase: form.endPhase,
      player1FinalLife: Number(form.player1FinalLife),
      player2FinalLife: Number(form.player2FinalLife)
    }).subscribe({
      next: () => {
        this.successMessage = 'Resultado registrado';
        this.load();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo registrar el resultado';
        this.cdr.markForCheck();
      }
    });
  }

  onNextRound(): void {
    this.errorMessage = '';
    this.tournamentService.nextRound(this.tournamentId).subscribe({
      next: (res) => {
        if (res.status === 'finished') {
          this.successMessage = `¡Torneo finalizado! Campeón: Mazo ${res.champion_deck_id}`;
          this.cdr.markForCheck();
        } else {
          this.router.navigate(['/tournaments', this.tournamentId, 'rounds', res.round_id]);
        }
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo avanzar de ronda';
        this.cdr.markForCheck();
      }
    });
  }

  getPlayerName(deckId: number): string {
    return this.playerNames[deckId] ?? `Mazo ${deckId}`;
  }

  private loadDeckOwner(deckId: number): void {
    if (this.playerNames[deckId]) return;
    this.deckService.getDeckById(deckId).subscribe({
      next: (deck) => {
        const player = this.allPlayers.find(p => p.playerId === deck.playerId);
        this.playerNames[deckId] = player ? player.name : `Mazo ${deckId}`;
        this.cdr.markForCheck();
      }
    });
  }

}