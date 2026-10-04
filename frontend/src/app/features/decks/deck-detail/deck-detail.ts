import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DeckService } from '../../../core/services/deck';
import { CardService } from '../../../core/services/card';
import { Deck, DeckCard, Card } from '../../../models/deck.model';

@Component({
  selector: 'app-deck-detail',
  imports: [],
  templateUrl: './deck-detail.html',
  styleUrl: './deck-detail.css'
})
export class DeckDetail implements OnInit {
  deck: Deck | null = null;
  allCards: Card[] = [];
  deckCards: DeckCard[] = [];
  errorMessage = '';
  successMessage = '';

  deckId!: number;

  constructor(
    private route: ActivatedRoute,
    private deckService: DeckService,
    private cardService: CardService,
    private cdr: ChangeDetectorRef
  ) {}

  get totalCards(): number {
    return this.deckCards.reduce((sum, dc) => sum + dc.quantity, 0);
  }

  ngOnInit(): void {
    this.deckId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadAll();
  }

  loadAll(): void {
    this.deckService.getMyDecks().subscribe({
      next: (decks) => {
        this.deck = decks.find(d => d.deckId === this.deckId) ?? null;
        this.cdr.markForCheck();
      }
    });

    this.cardService.getCards().subscribe({
      next: (cards) => {
        this.allCards = cards;
        this.cdr.markForCheck();
      }
    });

    this.deckService.getDeckCards(this.deckId).subscribe({
      next: (deckCards) => {
        this.deckCards = deckCards;
        this.cdr.markForCheck();
      }
    });
  }

  getQuantity(cardId: number): number {
    return this.deckCards.find(dc => dc.cardId === cardId)?.quantity ?? 0;
  }

  onAddCard(cardId: number, quantityStr: string): void {
    this.errorMessage = '';
    this.successMessage = '';
    const quantity = Number(quantityStr);

    this.deckService.addCardToDeck(this.deckId, cardId, quantity).subscribe({
      next: () => {
        this.successMessage = 'Carta agregada';
        this.loadAll();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo agregar la carta';
        this.cdr.markForCheck();
      }
    });
  }

  onUpdateQuantity(cardId: number, quantityStr: string): void {
    this.errorMessage = '';
    this.successMessage = '';
    const quantity = Number(quantityStr);

    this.deckService.updateCardQuantity(this.deckId, cardId, quantity).subscribe({
      next: () => {
        this.successMessage = 'Cantidad actualizada';
        this.loadAll();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo actualizar';
        this.cdr.markForCheck();
      }
    });
  }

  onRemoveCard(cardId: number): void {
    this.errorMessage = '';
    this.successMessage = '';

    this.deckService.removeCard(this.deckId, cardId).subscribe({
      next: () => {
        this.successMessage = 'Carta eliminada del mazo';
        this.loadAll();
      },
      error: () => {
        this.errorMessage = 'No se pudo eliminar';
        this.cdr.markForCheck();
      }
    });
  }

}