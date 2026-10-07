import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TournamentService } from '../../core/services/tournament';
import { MyStats } from '../../models/tournament.model';

@Component({
  selector: 'app-stats',
  imports: [RouterLink],
  templateUrl: './stats.html',
  styleUrl: './stats.css'
})
export class Stats implements OnInit {
  stats: MyStats | null = null;

  constructor(private tournamentService: TournamentService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.tournamentService.getMyStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.cdr.markForCheck();
      }
    });
  }
}