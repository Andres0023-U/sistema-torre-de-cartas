import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Deck, DeckCreate, DeckCard } from '../../models/deck.model';

@Injectable({
  providedIn: 'root'
})
export class DeckService {
  private apiUrl = `${environment.apiUrl}/decks`;

  constructor(private http: HttpClient) {}

  getMyDecks(): Observable<Deck[]> {
    return this.http.get<any[]>(`${this.apiUrl}/me`).pipe(
      map(list => list.map(d => ({
        deckId: d.deck_id,
        playerId: d.player_id,
        name: d.name
      })))
    );
  }

  createDeck(data: DeckCreate): Observable<Deck> {
    return this.http.post<any>(`${this.apiUrl}/`, { name: data.name }).pipe(
      map(d => ({ deckId: d.deck_id, playerId: d.player_id, name: d.name }))
    );
  }

  getDeckCards(deckId: number): Observable<DeckCard[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${deckId}/cards`).pipe(
      map(list => list.map(dc => ({
        deckId: dc.deck_id,
        cardId: dc.card_id,
        quantity: dc.quantity
      })))
    );
  }

  addCardToDeck(deckId: number, cardId: number, quantity: number): Observable<DeckCard> {
    return this.http.post<any>(`${this.apiUrl}/${deckId}/cards`, { card_id: cardId, quantity }).pipe(
      map(dc => ({ deckId: dc.deck_id, cardId: dc.card_id, quantity: dc.quantity }))
    );
  }

  updateCardQuantity(deckId: number, cardId: number, quantity: number): Observable<DeckCard> {
    return this.http.put<any>(`${this.apiUrl}/${deckId}/cards/${cardId}`, { card_id: cardId, quantity }).pipe(
      map(dc => ({ deckId: dc.deck_id, cardId: dc.card_id, quantity: dc.quantity }))
    );
  }

  removeCard(deckId: number, cardId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${deckId}/cards/${cardId}`);
  }

  getDeckById(deckId: number): Observable<Deck> {
    return this.http.get<any>(`${this.apiUrl}/${deckId}`).pipe(
      map(d => ({ deckId: d.deck_id, playerId: d.player_id, name: d.name }))
    );
  }
  
}