import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { PendingUser, AssignableRole } from '../../models/admin.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = `${environment.apiUrl}/auth`;

  constructor(private http: HttpClient) {}

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
}