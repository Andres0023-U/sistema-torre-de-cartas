import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth';

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home implements OnInit {
  userName = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.authService.getCurrentUser().subscribe({
      next: (user) => {
        this.userName = user.name;
        this.cdr.markForCheck();
      }
    });
  }

  get roleLabel(): string {
    const role = localStorage.getItem('role');
    if (role === 'organizer') return 'Organizador';
    if (role === 'admin') return 'Administrador';
    return 'Jugador';
  }

  get menuItems() {
    return [
      { path: '/tournaments', title: 'Torneos', description: 'Ver, crear y gestionar torneos' },
      { path: '/decks', title: 'Mis mazos', description: 'Construye y edita tus mazos de combate' }
    ];
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}