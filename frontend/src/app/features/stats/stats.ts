import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TournamentService } from '../../core/services/tournament';
import { MyStats, HistoryEntry } from '../../models/tournament.model';

@Component({
  selector: 'app-stats',
  imports: [RouterLink, DatePipe],
  templateUrl: './stats.html',
  styleUrl: './stats.css'
})
export class Stats implements OnInit {
  stats: MyStats | null = null;
  history: HistoryEntry[] = [];
  historyLoaded = false;

  constructor(private tournamentService: TournamentService, private cdr: ChangeDetectorRef) {}

  get tournamentsPlayed(): number {
    return new Set(this.history.map(h => h.tournamentId)).size;
  }

  ngOnInit(): void {
    this.tournamentService.getMyStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.cdr.markForCheck();
      }
    });

    this.tournamentService.getMyHistory().subscribe({
      next: (data) => {
        this.history = data;
        this.historyLoaded = true;
        this.cdr.markForCheck();
      },
      error: () => {
        this.historyLoaded = true;
        this.cdr.markForCheck();
      }
    });
  }
}