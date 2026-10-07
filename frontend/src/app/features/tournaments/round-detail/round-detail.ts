import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatchService } from '../../../core/services/match';
import { TournamentService } from '../../../core/services/tournament';
import { Match, Result, Round } from '../../../models/tournament.model';
import { PlayerService } from '../../../core/services/player';
import { DeckService } from '../../../core/services/deck';
import { Deck } from '../../../models/deck.model';
import { TournamentPlayer } from '../../../models/player.model';

@Component({
  selector: 'app-round-detail',
  imports: [FormsModule, RouterLink],
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
    private allPlayers: TournamentPlayer[] = [];
  myDecks: Deck[] = [];
  myDecksLoaded = false;
  deckTotals: Record<number, number> = {};
  currentDeckId: number | null = null;   // mazo ya guardado para esta ronda
  selectedDeckId: number | null = null;  // valor del selector
  deckDataLoaded = false;
  savingDeck = false;

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

  get isOrganizer(): boolean {
    return localStorage.getItem('role') === 'organizer';
  }

  get isPlayer(): boolean {
    return localStorage.getItem('role') === 'player';
  }

  get validDecks(): Deck[] {
    return this.myDecks.filter(d => (this.deckTotals[d.deckId] ?? 0) >= 20);
  }

  get decksLoaded(): boolean {
    return this.myDecksLoaded && Object.keys(this.deckTotals).length >= this.myDecks.length;
  }

  get roundOpenForDeckChange(): boolean {
    return this.round?.status === 'pending' && this.matches.length === 0;
  }

  get canChooseDeck(): boolean {
    return this.isPlayer && this.roundOpenForDeckChange &&
      (this.currentDeckId !== null || this.round?.number === 1);
  }

  get notInRound(): boolean {
    return this.isPlayer && this.deckDataLoaded && this.roundOpenForDeckChange &&
      this.currentDeckId === null && (this.round?.number ?? 1) > 1;
  }

  get allResultsIn(): boolean {
    return this.matches.length > 0 && this.matches.every(m => this.results[m.matchId]);
  }

  get canAdvance(): boolean {
    return this.isOrganizer && this.allResultsIn && this.round?.status !== 'finished';
  }

  get isLastRoundPossible(): boolean {
    return this.matches.length === 1;
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.tournamentId = Number(params.get('id'));
      this.roundId = Number(params.get('roundId'));
      this.matches = [];
      this.results = {};
      this.forms = {};
      this.round = null;
      this.currentDeckId = null;
      this.selectedDeckId = null;
      this.deckDataLoaded = false;
      this.myDecksLoaded = false;
      this.deckTotals = {};
      this.playerNames = {};
      this.allPlayers = [];

      this.tournamentService.getTournamentPlayers(this.tournamentId).subscribe({
        next: (players) => {
          this.allPlayers = players;
          this.load();
          this.loadMyDeckData();
        },
        error: (err) => {
          this.errorMessage = err.error?.detail || 'No se pudo cargar el torneo';
          this.cdr.markForCheck();
        }
      });
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
    this.successMessage = '';
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
    this.successMessage = '';
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
    this.successMessage = '';
    this.tournamentService.nextRound(this.tournamentId).subscribe({
      next: (res) => {
        if (res.status === 'finished') {
          this.successMessage = `¡Torneo finalizado! Campeón: ${this.getPlayerName(res.champion_deck_id)}`;
          this.load();
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
        this.playerNames[deckId] = player
          ? `${player.name} #${player.playerId}`
          : `Mazo ${deckId}`;
        this.cdr.markForCheck();
      }
    });
  }

  private loadMyDeckData(): void {
    if (!this.isPlayer) return;

    this.deckService.getMyDecks().subscribe({
      next: (decks) => {
        this.myDecks = decks;
        this.myDecksLoaded = true;
        decks.forEach(d => {
          this.deckService.getDeckCards(d.deckId).subscribe({
            next: (cards) => {
              this.deckTotals[d.deckId] = cards.reduce((sum, c) => sum + c.quantity, 0);
              this.cdr.markForCheck();
            }
          });
        });
        this.cdr.markForCheck();
      }
    });

    this.tournamentService.getMyDeckSelection(this.roundId).subscribe({
      next: (deckId) => {
        this.currentDeckId = deckId;
        this.selectedDeckId = deckId;
        this.deckDataLoaded = true;
        this.cdr.markForCheck();
      }
    });
  }

  getDeckName(deckId: number): string {
    return this.myDecks.find(d => d.deckId === deckId)?.name ?? `Mazo ${deckId}`;
  }

  onSaveDeck(): void {
    if (this.selectedDeckId === null) return;

    this.errorMessage = '';
    this.successMessage = '';
    this.savingDeck = true;

    this.tournamentService.selectDeck(this.roundId, this.selectedDeckId).subscribe({
      next: () => {
        this.currentDeckId = this.selectedDeckId;
        this.successMessage = 'Mazo guardado para esta ronda';
        this.savingDeck = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo guardar el mazo';
        this.savingDeck = false;
        this.cdr.markForCheck();
      }
    });
  }

}