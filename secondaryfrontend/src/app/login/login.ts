import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  credentials = {
    username: '',
    password: '',
    email: ''
  };

  isSignup = signal(false);
  successMessage = signal('');
  isLoading = signal(false);

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    // If already authenticated, go to chat
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/chat']);
    }
  }

  toggleSignup(): void {
    this.isSignup.update(v => !v);
    this.successMessage.set('');
    this.credentials = { username: '', password: '', email: '' };
  }

  async submit(): Promise<void> {
    if (!this.credentials.username.trim() || !this.credentials.password.trim()) {
      alert('Please enter username and password');
      return;
    }

    if (this.isSignup() && !this.credentials.email.trim()) {
      alert('Please enter email for signup');
      return;
    }

    this.successMessage.set('');
    this.isLoading.set(true);

    try {
      if (this.isSignup()) {
        await this.authService.register(
          this.credentials.email,
          this.credentials.username,
          this.credentials.password
        );
        this.isLoading.set(false);
        this.isSignup.set(false);
        this.successMessage.set('Account created! Please log in.');
        this.credentials.password = '';
      } else {
        await this.authService.login(this.credentials.username, this.credentials.password);
        this.isLoading.set(false);
        this.router.navigate(['/chat']);
      }
    } catch (err: any) {
      this.isLoading.set(false);
      const errorData = err?.error || err;
      alert(errorData?.message || errorData?.error || (this.isSignup() ? 'Signup failed. Please try again.' : 'Login failed. Please try again.'));
    }
  }

  handleKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.submit();
    }
  }
}
