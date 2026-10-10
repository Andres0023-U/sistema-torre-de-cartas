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

  showForm = false;

  readonly filters: { value: string; label: string }[] = [
    { value: 'all', label: 'Todos' },
    { value: 'pending', label: 'Pendiente' },
    { value: 'in_progress', label: 'En curso' },
    { value: 'finished', label: 'Finalizado' }
  ];

  countByStatus(value: string): number {
    if (value === 'all') return this.tournaments.length;
    return this.tournaments.filter(t => t.status === value).length;
  }

  badgeClass(status: string): string {
    switch (status) {
      case 'pending':
        return 'bg-amber-100 text-amber-800';
      case 'in_progress':
        return 'bg-emerald-100 text-emerald-800';
      case 'finished':
        return 'bg-slate-200 text-slate-700';
      default:
        return 'bg-slate-100 text-slate-600';
    }
  }

  formatDate(date: string): string {
    const d = new Date(date + 'T00:00:00');
    if (isNaN(d.getTime())) return date;
    return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' });
  }

}