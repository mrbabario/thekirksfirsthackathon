import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';

type Language = 'en' | 'ms' | 'zh';

@Component({
  selector: 'app-create-post',
  standalone: true,

  imports: [
    RouterLink,
    FormsModule,
    HlmButtonImports,
    HlmDropdownMenuImports,
    HlmInputImports,
    HlmTextareaImports,
  ],

  templateUrl: './create-post.html',
  styleUrl: './create-post.css',
})
export class CreatePost {
  // ==========================================
  // LANGUAGE
  // ==========================================

  language = 'English';

  setLanguage(language: Language): void {
    switch (language) {
      case 'en':
        this.language = 'English';
        break;

      case 'ms':
        this.language = 'Bahasa Melayu';
        break;

      case 'zh':
        this.language = '中文';
        break;
    }
  }

  // ==========================================
  // FORM
  // ==========================================

  title = '';
  category = 'General Discussion';
  tag = 'Cancer';
  content = '';

  categories = ['General Discussion', 'Fact Checking', 'Media & News', 'Help & Feedback'];

  tags = [
    'Cancer',
    'Heart Disease',
    'Diabetes',
    'Mental Health',
    'Infectious Diseases',
    'Nutrition',
    'Women Health',
    'Men Health',
    'Children Health',
    'Neurology',
    'Respiratory Health',
    'Medical Research',
    'Medications',
    'Public Health',
    'Other',
  ];

  constructor(private router: Router) {}

  // ==========================================
  // SUBMIT
  // ==========================================

  submitPost(): void {
  if (!this.title.trim() || !this.content.trim()) {
    return;
  }

  this.router.navigate(['/asdf-post']);
}
}
