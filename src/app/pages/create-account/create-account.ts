import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';

@Component({
  selector: 'app-create-account',
  imports: [
    FormsModule,
    RouterLink,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
  ],
  templateUrl: './create-account.html',
  styleUrl: './create-account.css',
})
export class CreateAccount {
  name = '';
  email = '';
  password = '';
  confirmPassword = '';

  errorMessage = '';

  constructor(
    private router: Router,
    private authService: AuthService,
  ) {}

  onSubmit() {
    this.errorMessage = '';

    // Check passwords before sending request
    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Passwords do not match';
      return;
    }

    this.authService
      .register({
        full_name: this.name,
        email: this.email,
        password: this.password,
        confirm_password: this.confirmPassword,
      })
      .subscribe({
        next: (response) => {
          console.log('Account created successfully:', response);

          // Redirect only after successful registration
          this.router.navigate(['/sign-in']);
        },

        error: (error) => {
          console.error('Registration failed:', error);

          const detail = error.error?.detail;

          if (Array.isArray(detail)) {
            this.errorMessage = detail.map((item) => item.msg).join(', ');
          } else {
            this.errorMessage = detail || 'Something went wrong. Please try again.';
          }
        },
      });
  }
}
