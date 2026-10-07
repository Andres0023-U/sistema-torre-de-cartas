import { Component, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth';

@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  email = '';
  password = '';
  errorMessage = '';
  submitted = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  get emailMissing(): boolean {
    return this.submitted && !this.email.trim();
  }

  get passwordMissing(): boolean {
    return this.submitted && !this.password;
  }

  onSubmit(): void {
    this.submitted = true;
    this.errorMessage = '';

    if (!this.email.trim() || !this.password) {
      return;
    }

    this.authService.login({ email: this.email.trim(), password: this.password }).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (err) => {
        if (err.status === 0) {
          this.errorMessage = 'No se pudo conectar con el servidor. Intenta de nuevo en unos segundos.';
        } else if (err.status === 403) {
          this.errorMessage = err.error?.detail || 'Tu cuenta está desactivada.';
        } else {
          this.errorMessage = 'Correo o contraseña incorrectos';
        }
        this.cdr.markForCheck();
      }
    });
  }
}