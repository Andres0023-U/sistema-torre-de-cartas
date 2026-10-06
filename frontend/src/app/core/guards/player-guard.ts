import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';

export const playerGuard: CanActivateFn = () => {
  const router = inject(Router);

  if (localStorage.getItem('role') === 'player') {
    return true;
  }

  router.navigate(['/']);
  return false;
};