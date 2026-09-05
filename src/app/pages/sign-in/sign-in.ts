import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmLabelImports } from '@spartan-ng/helm/label';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-sign-in',
  imports: [
    FormsModule,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmLabelImports,
    RouterLink,
  ],
  templateUrl: './sign-in.html',
  styleUrl: './sign-in.css',
})
export class SignIn {
  email = '';
  password = '';

  onSubmit() {
    console.log('Email:', this.email);
    console.log('Password:', this.password);

    // Add your actual authentication logic here later.
  }
}
