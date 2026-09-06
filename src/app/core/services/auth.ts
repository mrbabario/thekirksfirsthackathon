import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  confirm_password: string;
}


export interface RegisterResponse {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
}


export interface LoginRequest {
  email: string;
  password: string;
}


export interface LoginResponse {
  access_token: string;
  token_type: string;

  user_id: number;
  full_name: string;
  email: string;
}


@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);

  private readonly API_URL = 'http://localhost:8000/api/auth';


  register(data: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(
      `${this.API_URL}/register`,
      data,
    );
  }


  login(data: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.API_URL}/login`,
      data,
    );
  }


  saveLogin(response: LoginResponse): void {
    localStorage.setItem(
      'access_token',
      response.access_token,
    );

    localStorage.setItem(
      'user',
      JSON.stringify({
        id: response.user_id,
        full_name: response.full_name,
        email: response.email,
      }),
    );
  }


  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }


  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }


  getUser(): {
    id: number;
    full_name: string;
    email: string;
  } | null {

    const user = localStorage.getItem('user');

    if (!user) {
      return null;
    }

    return JSON.parse(user);
  }
}
