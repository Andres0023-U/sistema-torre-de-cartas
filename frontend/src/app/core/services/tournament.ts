import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Tournament, TournamentCreate } from '../../models/tournament.model';

@Injectable({
  providedIn: 'root'
})
export class TournamentService {
  private apiUrl = 'http://127.0.0.1:8000/tournaments';

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
}