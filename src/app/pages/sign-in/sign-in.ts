import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/services/auth';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';


@Component({
  selector: 'app-sign-in',
  imports: [
    FormsModule,
    RouterLink,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
  ],
  templateUrl: './sign-in.html',
  styleUrl: './sign-in.css',
})
export class SignIn {
  email = '';
  password = '';

  errorMessage = '';


  constructor(
    private router: Router,
    private authService: AuthService,
  ) {}


  onSubmit() {
    this.errorMessage = '';

    this.authService.login({
      email: this.email,
      password: this.password,
    }).subscribe({
      next: (response) => {
        console.log('Login successful:', response);

        // Save login information
        this.authService.saveLogin(response);

        // Temporarily redirect after successful login
        this.router.navigate(['/']);
      },

      error: (error) => {
        console.error('Login failed:', error);

        const detail = error.error?.detail;

        if (Array.isArray(detail)) {
          this.errorMessage = detail
            .map((item) => item.msg)
            .join(', ');
        } else {
          this.errorMessage =
            detail || 'Something went wrong. Please try again.';
        }
      },
    });
  }
}
