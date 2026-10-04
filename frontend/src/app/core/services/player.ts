import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PlayerWithUser } from '../../models/player.model';

@Injectable({
  providedIn: 'root'
})
export class PlayerService {
  private apiUrl = `${environment.apiUrl}/players`;

  constructor(private http: HttpClient) {}

  getPlayers(): Observable<PlayerWithUser[]> {
    return this.http.get<any[]>(`${this.apiUrl}/`).pipe(
      map(list => list.map(p => ({
        playerId: p.player_id,
        userId: p.user_id,
        name: p.name,
        email: p.email
      })))
    );
  }
}