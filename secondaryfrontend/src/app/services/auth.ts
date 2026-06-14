import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiBase = environment.apiBaseUrl;
  private currentUser = signal<string | null>(null);
  private authenticated = signal(false);

  readonly isAuthenticated = computed(() => this.authenticated());
  readonly user = computed(() => this.currentUser());

  constructor(private http: HttpClient) {}

  async login(username: string, password: string): Promise<any> {
    const response = await firstValueFrom(
      this.http.post<any>(`${this.apiBase}/login`, { username, password }, { withCredentials: true })
    );
    if (response.status === 'success') {
      this.currentUser.set(response.username);
      this.authenticated.set(true);
    }
    return response;
  }

  async register(email: string, username: string, password: string): Promise<any> {
    const response = await firstValueFrom(
      this.http.post<any>(`${this.apiBase}/register`, { email, username, password }, { withCredentials: true })
    );
    return response;
  }

  async logout(): Promise<any> {
    const response = await firstValueFrom(
      this.http.post<any>(`${this.apiBase}/logout`, {}, { withCredentials: true })
    );
    this.currentUser.set(null);
    this.authenticated.set(false);
    return response;
  }

  async checkAuth(): Promise<any> {
    try {
      const response = await firstValueFrom(
        this.http.get<any>(`${this.apiBase}/check-auth`, { withCredentials: true })
      );
      if (response.authenticated) {
        this.currentUser.set(response.username);
        this.authenticated.set(true);
      } else {
        this.currentUser.set(null);
        this.authenticated.set(false);
      }
      return response;
    } catch {
      this.currentUser.set(null);
      this.authenticated.set(false);
      return { authenticated: false };
    }
  }

  getCurrentUser(): string | null {
    return this.currentUser();
  }
}
