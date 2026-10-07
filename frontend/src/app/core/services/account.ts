import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AccountService {
  private apiUrl = `${environment.apiUrl}/auth`;

  constructor(private http: HttpClient) {}

  updateName(name: string): Observable<{ user_id: number; name: string }> {
    return this.http.put<{ user_id: number; name: string }>(`${this.apiUrl}/me/name`, { name });
  }
}