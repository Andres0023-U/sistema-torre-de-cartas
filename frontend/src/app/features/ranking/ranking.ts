import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink } from '@angular/router';
import { GlobalRankingEntry } from '../../models/tournament.model';
import { TournamentService } from '../../core/services/tournament';

@Component({
  selector: 'app-ranking',
  imports: [RouterLink],
  templateUrl: './ranking.html',
  styleUrl: './ranking.css'
})
export class Ranking implements OnInit {
  ranking: GlobalRankingEntry[] = [];

  constructor(private tournamentService: TournamentService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.tournamentService.getGlobalRanking().subscribe({
      next: (data) => {
        this.ranking = data;
        this.cdr.markForCheck();
      }
    });
  }
}