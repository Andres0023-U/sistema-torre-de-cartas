import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Match, Result, ResultCreate } from '../../models/tournament.model';

@Injectable({
  providedIn: 'root'
})
export class MatchService {
  private matchesUrl = `${environment.apiUrl}/matches`;

  constructor(private http: HttpClient) {}

  private mapMatch(m: any): Match {
    return { matchId: m.match_id, roundId: m.round_id, deck1Id: m.deck1_id, deck2Id: m.deck2_id };
  }

  private mapResult(r: any): Result {
    return {
      resultId: r.result_id,
      matchId: r.match_id,
      winnerId: r.winner_id,
      endPhase: r.end_phase,
      player1FinalLife: r.player1_final_life,
      player2FinalLife: r.player2_final_life,
      player1Points: r.player1_points,
      player2Points: r.player2_points,
      date: r.date
    };
  }

  getMatchesByRound(roundId: number): Observable<Match[]> {
    return this.http.get<any[]>(`${this.matchesUrl}/?round_id=${roundId}`).pipe(
      map(list => list.map(m => this.mapMatch(m)))
    );
  }

  generateMatches(roundId: number): Observable<Match[]> {
    return this.http.post<any[]>(`${this.matchesUrl}/generate/${roundId}`, {}).pipe(
      map(list => list.map(m => this.mapMatch(m)))
    );
  }

  getResult(matchId: number): Observable<Result | null> {
    return this.http.get<any>(`${this.matchesUrl}/${matchId}/result`).pipe(
      map(r => this.mapResult(r))
    );
  }

  createResult(matchId: number, data: ResultCreate): Observable<Result> {
    const body = {
      winner_id: data.winnerId,
      end_phase: data.endPhase,
      player1_final_life: data.player1FinalLife,
      player2_final_life: data.player2FinalLife
    };
    return this.http.post<any>(`${this.matchesUrl}/${matchId}/result`, body).pipe(
      map(r => this.mapResult(r))
    );
  }
}