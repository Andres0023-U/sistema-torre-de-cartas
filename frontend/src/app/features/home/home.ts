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
    if (role === 'pending') return 'Pendiente de aprobación';
    return 'Jugador';
  }

  get isPending(): boolean {
    return localStorage.getItem('role') === 'pending';
  }

  get menuItems() {
    const role = localStorage.getItem('role');
    const items = [
      { path: '/tournaments', title: 'Torneos', description: 'Ver, crear y gestionar torneos' }
    ];

    if (role === 'player') {
      items.push({
        path: '/decks',
        title: 'Mis mazos',
        description: 'Construye y edita tus mazos de combate'
      });
    }

    if (role === 'admin') {
      items.unshift({
        path: '/admin',
        title: 'Administración',
        description: 'Aprueba usuarios nuevos y asigna sus roles'
      });
    }

    return items;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}