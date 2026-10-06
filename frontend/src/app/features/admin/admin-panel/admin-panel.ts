import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AdminService } from '../../../core/services/admin';
import { PendingUser, AssignableRole } from '../../../models/admin.model';

@Component({
  selector: 'app-admin-panel',
  imports: [RouterLink],
  templateUrl: './admin-panel.html'
})
export class AdminPanel implements OnInit {
  users: PendingUser[] = [];
  loading = true;
  processingId: number | null = null;
  errorMessage = '';
  successMessage = '';

  constructor(
    private adminService: AdminService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;
    this.errorMessage = '';

    this.adminService.getPendingUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudieron cargar los usuarios.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  assign(user: PendingUser, role: AssignableRole): void {
    this.processingId = user.userId;
    this.errorMessage = '';
    this.successMessage = '';

    this.adminService.assignRole(user.userId, role).subscribe({
      next: () => {
        this.users = this.users.filter(u => u.userId !== user.userId);
        const label = role === 'organizer' ? 'organizador' : 'jugador';
        this.successMessage = `${user.name} ahora es ${label}.`;
        this.processingId = null;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo asignar el rol.';
        this.processingId = null;
        this.cdr.markForCheck();
      }
    });
  }
}