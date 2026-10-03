import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TournamentService } from '../../../core/services/tournament';
import { Tournament } from '../../../models/tournament.model';

@Component({
  selector: 'app-tournament-list',
  imports: [FormsModule],
  templateUrl: './tournament-list.html',
  styleUrl: './tournament-list.css'
})
export class TournamentList implements OnInit {
  tournaments: Tournament[] = [];
  name = '';
  date = '';
  numPlayers = 8;
  errorMessage = '';
  successMessage = '';

  constructor(
    private tournamentService: TournamentService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadTournaments();
  }

  loadTournaments(): void {
    this.tournamentService.getTournaments().subscribe({
      next: (data) => {
        this.tournaments = data;
        this.cdr.markForCheck();
      }
    });
  }

  onCreate(): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.tournamentService.createTournament({
      name: this.name,
      date: this.date,
      format: 'single_elimination',
      numPlayers: this.numPlayers
    }).subscribe({
      next: () => {
        this.successMessage = 'Torneo creado correctamente';
        this.name = '';
        this.date = '';
        this.loadTournaments();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.status === 403
          ? 'Solo los organizadores pueden crear torneos'
          : 'Error al crear el torneo';
        this.cdr.markForCheck();
      }
    });
  }
}