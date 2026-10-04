import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Tournament, TournamentCreate } from '../../models/tournament.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TournamentService {
  private apiUrl = `${environment.apiUrl}/tournaments`;

  constructor(private http: HttpClient) {}

  private mapTournament(t: any): Tournament {
    return {
      tournamentId: t.tournament_id,
      name: t.name,
      date: t.date,
      format: t.format,
      numPlayers: t.num_players,
      status: t.status,
      organizerId: t.organizer_id
    };
  }

  getTournaments(): Observable<Tournament[]> {
    return this.http.get<any[]>(`${this.apiUrl}/`).pipe(
      map(list => list.map(t => this.mapTournament(t)))
    );
  }

  createTournament(data: TournamentCreate): Observable<Tournament> {
    const body = {
      name: data.name,
      date: data.date,
      format: data.format,
      num_players: data.numPlayers
    };

    return this.http.post<any>(`${this.apiUrl}/`, body).pipe(
      map(t => this.mapTournament(t))
    );
  }

  getRegisteredPlayers(tournamentId: number): Observable<number[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${tournamentId}/registrations`).pipe(
      map(list => list.map(r => r.player_id))
    );
  }

  registerPlayer(tournamentId: number, playerId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${tournamentId}/registrations`, { player_id: playerId });
  }

  startTournament(tournamentId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${tournamentId}/start`, {});
  }
}