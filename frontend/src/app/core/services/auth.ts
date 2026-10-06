import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, map } from 'rxjs';
import { LoginRequest, LoginResponse } from '../../models/auth.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;

  constructor(private http: HttpClient) {}

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<any>(`${this.apiUrl}/login`, credentials).pipe(
      map(response => ({
        accessToken: response.access_token,
        tokenType: response.token_type,
        role: response.role
      } as LoginResponse)),
      tap(response => {
        localStorage.setItem('access_token', response.accessToken);
        localStorage.setItem('role', response.role);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('role');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getCurrentUser(): Observable<{ userId: string; role: string; name: string }> {
    return this.http.get<any>(`${this.apiUrl}/me`).pipe(
      map(u => ({ userId: u.user_id, role: u.role, name: u.name }))
    );
  }
}