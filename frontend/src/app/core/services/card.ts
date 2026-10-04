import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Card } from '../../models/deck.model';

@Injectable({
  providedIn: 'root'
})
export class CardService {
  private apiUrl = `${environment.apiUrl}/cards`;

  constructor(private http: HttpClient) {}

  getCards(): Observable<Card[]> {
    return this.http.get<any[]>(`${this.apiUrl}/`).pipe(
      map(list => list.map(c => ({
        cardId: c.card_id,
        cardName: c.card_name,
        value: c.value,
        type: c.type,
        effect: c.effect,
        maxQuantity: c.max_quantity,
        rarity: c.rarity,
        description: c.description
      })))
    );
  }
}