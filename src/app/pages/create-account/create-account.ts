import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

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

  constructor(private router: Router) {}

  onSubmit() {
    if (this.password !== this.confirmPassword) {
      console.log('Passwords do not match');
      return;
    }

    // Account creation logic goes here.
    console.log('Account created successfully');

    // Redirect to sign-in page
    this.router.navigate(['/sign-in']);
  }
}
