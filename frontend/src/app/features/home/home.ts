import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth';

interface MenuItem {
  path: string;
  title: string;
  description: string;
  icon: 'trophy' | 'ranking' | 'deck' | 'stats' | 'account' | 'admin';
}

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

  get menuItems(): MenuItem[] {
    const role = localStorage.getItem('role');

    const items: MenuItem[] = [
      {
        path: '/tournaments',
        title: 'Torneos',
        description: role === 'organizer' ? 'Crea y gestiona tus torneos' : 'Consulta los torneos disponibles',
        icon: 'trophy'
      },
      {
        path: '/ranking',
        title: 'Ranking',
        description: 'Clasificación global de jugadores',
        icon: 'ranking'
      }
    ];

    if (role === 'player') {
      items.push({
        path: '/decks',
        title: 'Mis mazos',
        description: 'Construye y edita tus mazos de combate',
        icon: 'deck'
      });

      items.push({
        path: '/stats',
        title: 'Mis estadísticas',
        description: 'Tu progreso, puntos y torneos ganados',
        icon: 'stats'
      });
    }

    items.push({
      path: '/account',
      title: 'Mi cuenta',
      description: 'Cambia tu nombre de usuario',
      icon: 'account'
    });

    if (role === 'admin') {
      items.unshift({
        path: '/admin',
        title: 'Administración',
        description: 'Aprueba usuarios nuevos y asigna sus roles',
        icon: 'admin'
      });
    }

    return items;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}