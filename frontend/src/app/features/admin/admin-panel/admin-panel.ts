import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AdminService } from '../../../core/services/admin';
import { PendingUser, AssignableRole, AdminUser } from '../../../models/admin.model';

@Component({
  selector: 'app-admin-panel',
  imports: [RouterLink],
  templateUrl: './admin-panel.html'
})
export class AdminPanel implements OnInit {
  users: PendingUser[] = [];
  allUsers: AdminUser[] = [];
  loading = true;
  usersLoading = true;
  processingId: number | null = null;
  togglingId: number | null = null;
  errorMessage = '';
  successMessage = '';

  constructor(
    private adminService: AdminService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadUsers();
    this.loadAllUsers();
  }

  roleLabel(role: string): string {
    switch (role) {
      case 'admin': return 'Administrador';
      case 'organizer': return 'Organizador';
      case 'player': return 'Jugador';
      case 'pending': return 'Pendiente';
      default: return role;
    }
  }

  loadUsers(): void {
    this.loading = true;

    this.adminService.getPendingUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudieron cargar los usuarios pendientes.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  loadAllUsers(): void {
    this.usersLoading = true;

    this.adminService.getUsers().subscribe({
      next: (users) => {
        this.allUsers = users;
        this.usersLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo cargar la lista de usuarios.';
        this.usersLoading = false;
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
        this.loadAllUsers();
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo asignar el rol.';
        this.processingId = null;
        this.cdr.markForCheck();
      }
    });
  }

  toggleActive(user: AdminUser): void {
    this.togglingId = user.userId;
    this.errorMessage = '';
    this.successMessage = '';

    this.adminService.setActive(user.userId, !user.isActive).subscribe({
      next: (updated) => {
        this.allUsers = this.allUsers.map(u => u.userId === updated.userId ? updated : u);
        this.successMessage = updated.isActive
          ? `${updated.name} fue reactivado.`
          : `${updated.name} fue desactivado.`;
        this.togglingId = null;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'No se pudo cambiar el estado de la cuenta.';
        this.togglingId = null;
        this.cdr.markForCheck();
      }
    });
  }
}