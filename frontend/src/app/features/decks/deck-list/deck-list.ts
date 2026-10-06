import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { DeckService } from '../../../core/services/deck';
import { Deck } from '../../../models/deck.model';

@Component({
  selector: 'app-deck-list',
  imports: [FormsModule, RouterLink],
  templateUrl: './deck-list.html',
  styleUrl: './deck-list.css'
})
export class DeckList implements OnInit {
  decks: Deck[] = [];
  name = '';

  constructor(private deckService: DeckService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.deckService.getMyDecks().subscribe({
      next: (data) => {
        this.decks = data;
        this.cdr.markForCheck();
      }
    });
  }

  onCreate(): void {
    const name = this.name.trim();
    if (!name) {
      return;
    }

    this.deckService.createDeck({ name }).subscribe({
      next: () => {
        this.name = '';
        this.load();
      }
    });
  }
}