import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { PendingUser, AssignableRole, AdminUser } from '../../models/admin.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = `${environment.apiUrl}/auth`;

  constructor(private http: HttpClient) {}

  private mapUser(u: any): AdminUser {
    return {
      userId: u.user_id,
      name: u.name,
      email: u.email,
      role: u.role,
      isActive: u.is_active
    };
  }

  getPendingUsers(): Observable<PendingUser[]> {
    return this.http.get<any[]>(`${this.apiUrl}/pending-users`).pipe(
      map(list => list.map(u => ({
        userId: u.user_id,
        name: u.name,
        email: u.email
      })))
    );
  }

  assignRole(userId: number, role: AssignableRole): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/${userId}/role`, { role });
  }

  getUsers(): Observable<AdminUser[]> {
    return this.http.get<any[]>(`${this.apiUrl}/users`).pipe(
      map(list => list.map(u => this.mapUser(u)))
    );
  }

  setActive(userId: number, isActive: boolean): Observable<AdminUser> {
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/active`, { is_active: isActive }).pipe(
      map(u => this.mapUser(u))
    );
  }
}