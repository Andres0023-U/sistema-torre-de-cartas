import { Component, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink, Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth';

@Component({
  selector: 'app-register',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  name = '';
  email = '';
  password = '';
  errorMessage = '';
  submitted = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  get nameError(): string {
    if (!this.submitted) return '';
    if (!this.name.trim()) return 'Este campo es obligatorio';
    return '';
  }

  get emailError(): string {
    if (!this.submitted) return '';
    const email = this.email.trim();
    if (!email) return 'Este campo es obligatorio';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Ingresa un correo válido';
    return '';
  }

  get passwordError(): string {
    if (!this.submitted) return '';
    if (!this.password) return 'Este campo es obligatorio';
    if (this.password.length < 8) return 'Debe tener al menos 8 caracteres';
    if (!/\p{L}/u.test(this.password)) return 'Debe incluir al menos una letra';
    if (!/\d/.test(this.password)) return 'Debe incluir al menos un número';
    return '';
  }

  onSubmit(): void {
    this.submitted = true;
    this.errorMessage = '';

    if (this.nameError || this.emailError || this.passwordError) {
      return;
    }

    this.authService.register({
      name: this.name.trim(),
      email: this.email.trim(),
      password: this.password
    }).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (err) => {
        const detail = err.error?.detail;
        if (err.status === 0) {
          this.errorMessage = 'No se pudo conectar con el servidor. Intenta de nuevo en unos segundos.';
        } else if (typeof detail === 'string') {
          this.errorMessage = detail;
        } else if (Array.isArray(detail)) {
          this.errorMessage = 'Revisa los datos ingresados.';
        } else {
          this.errorMessage = 'No se pudo crear la cuenta';
        }
        this.cdr.markForCheck();
      }
    });
  }
}