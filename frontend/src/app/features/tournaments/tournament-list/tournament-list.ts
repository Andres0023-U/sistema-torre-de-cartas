import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TournamentService } from '../../../core/services/tournament';
import { Tournament } from '../../../models/tournament.model';
import { RouterLink } from '@angular/router';
import { StatusLabelPipe } from '../../../shared/pipes/status-label';

@Component({
  selector: 'app-tournament-list',
  imports: [FormsModule, RouterLink, StatusLabelPipe],
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

  get isOrganizer(): boolean {
    const role = localStorage.getItem('role');
    return role === 'organizer' || role === 'admin';
  }

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

    const name = this.name.trim();
    if (!name || !this.date) {
      return;
    }

    this.tournamentService.createTournament({
      name,
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

  statusFilter: 'all' | 'pending' | 'in_progress' | 'finished' = 'all';

  get filteredTournaments(): Tournament[] {
    if (this.statusFilter === 'all') return this.tournaments;
    return this.tournaments.filter(t => t.status === this.statusFilter);
  }

  setStatusFilter(value: string): void {
    if (value === 'all' || value === 'pending' || value === 'in_progress' || value === 'finished') {
      this.statusFilter = value;
    }
  }

}