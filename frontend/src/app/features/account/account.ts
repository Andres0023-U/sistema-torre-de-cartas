import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth';
import { AccountService } from '../../core/services/account';

@Component({
  selector: 'app-account',
  imports: [FormsModule, RouterLink],
  templateUrl: './account.html'
})
export class Account implements OnInit {
  name = '';
  savedName = '';
  submitted = false;
  saving = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private authService: AuthService,
    private accountService: AccountService,
    private cdr: ChangeDetectorRef
  ) {}

  get roleLabel(): string {
    const role = localStorage.getItem('role');
    if (role === 'organizer') return 'Organizador';
    if (role === 'admin') return 'Administrador';
    if (role === 'pending') return 'Pendiente de aprobación';
    return 'Jugador';
  }

  get nameError(): string {
    if (!this.submitted) return '';
    if (!this.name.trim()) return 'Este campo es obligatorio';
    return '';
  }

  get unchanged(): boolean {
    return this.name.trim() === this.savedName;
  }

  ngOnInit(): void {
    this.authService.getCurrentUser().subscribe({
      next: (user) => {
        this.name = user.name;
        this.savedName = user.name;
        this.cdr.markForCheck();
      }
    });
  }

  onSubmit(): void {
    this.submitted = true;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.nameError || this.unchanged) {
      return;
    }

    this.saving = true;
    this.accountService.updateName(this.name.trim()).subscribe({
      next: (res) => {
        this.name = res.name;
        this.savedName = res.name;
        this.submitted = false;
        this.saving = false;
        this.successMessage = 'Nombre actualizado correctamente';
        this.cdr.markForCheck();
      },
      error: (err) => {
        const detail = err.error?.detail;
        this.errorMessage = typeof detail === 'string'
          ? detail
          : 'No se pudo actualizar el nombre. Revisa que no supere 20 caracteres.';
        this.saving = false;
        this.cdr.markForCheck();
      }
    });
  }
}