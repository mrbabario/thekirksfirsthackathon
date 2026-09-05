import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';

type Language = 'en' | 'ms' | 'zh';

@Component({
  selector: 'app-homepage',
  standalone: true,
  imports: [
    RouterLink,
    FormsModule,
    HlmButtonImports,
    HlmDropdownMenuImports,
    HlmInputImports,
    HlmTextareaImports
  ],
  templateUrl: './homepage.html',
  styleUrl: './homepage.css'
})
export class Homepage {

  language = signal<Language>('en');

  articleText = '';
  articleUrl = '';

  reviewing = signal(false);
  reviewResult = signal('');

  translations = {
    en: {
      home: 'Home',
      howItWorks: 'How It Works',
      about: 'About',
      language: 'Language',

      badge: 'AI-Powered Article Review',

      title: 'Understand your article.',
      titleHighlight: 'Before you trust it.',

      description:
        'Dr.Kirk helps you review articles for clarity, credibility, bias, and important claims.',

      textLabel: 'Paste your article',
      textPlaceholder:
        'Paste the article text you want Dr.Kirk to review...',

      urlLabel: 'Or review an article URL',
      urlPlaceholder:
        'https://example.com/article',

      review: 'Review',

      textHint: 'Paste the article text here.',
      urlHint: 'Enter the URL of the article you want to review.',

      resultTitle: 'Review Result',

      resultPlaceholder:
        'Your article review will appear here.',

      reviewing: 'Reviewing...',

      sampleResult:
        'This is a sample review. Your article has been submitted successfully. Dr.Kirk can analyze its clarity, claims, potential bias, and credibility.'
    },

    ms: {
      home: 'Laman Utama',
      howItWorks: 'Cara Ia Berfungsi',
      about: 'Tentang',
      language: 'Bahasa',

      badge: 'Semakan Artikel Berkuasa AI',

      title: 'Fahami artikel anda.',
      titleHighlight: 'Sebelum mempercayainya.',

      description:
        'Dr.Kirk membantu anda menyemak artikel dari segi kejelasan, kredibiliti, bias dan dakwaan penting.',

      textLabel: 'Tampal artikel anda',
      textPlaceholder:
        'Tampal teks artikel yang ingin anda semak...',

      urlLabel: 'Atau semak URL artikel',
      urlPlaceholder:
        'https://example.com/article',

      review: 'Semak',

      textHint: 'Tampal teks artikel di sini.',
      urlHint: 'Masukkan URL artikel yang ingin anda semak.',

      resultTitle: 'Keputusan Semakan',

      resultPlaceholder:
        'Semakan artikel anda akan muncul di sini.',

      reviewing: 'Sedang menyemak...',

      sampleResult:
        'Ini ialah contoh semakan. Artikel anda telah berjaya dihantar. Dr.Kirk boleh menganalisis kejelasan, dakwaan, kemungkinan bias dan kredibiliti.'
    },

    zh: {
      home: '首页',
      howItWorks: '使用方法',
      about: '关于',

      language: '语言',

      badge: 'AI 智能文章审查',

      title: '了解你的文章。',
      titleHighlight: '在相信它之前。',

      description:
        'Dr.Kirk 帮助你检查文章的清晰度、可信度、偏见以及重要论点。',

      textLabel: '粘贴你的文章',
      textPlaceholder:
        '粘贴你想让 Dr.Kirk 审查的文章内容...',

      urlLabel: '或者输入文章网址',
      urlPlaceholder:
        'https://example.com/article',

      review: '审查',

      textHint: '在这里粘贴文章内容。',
      urlHint: '输入你想审查的文章网址。',

      resultTitle: '审查结果',

      resultPlaceholder:
        '你的文章审查结果将在这里显示。',

      reviewing: '正在审查...',

      sampleResult:
        '这是一个示例审查结果。你的文章已经成功提交。Dr.Kirk 可以分析文章的清晰度、论点、潜在偏见以及可信度。'
    }
  };

  t() {
    return this.translations[this.language()];
  }

  setLanguage(language: Language) {
    this.language.set(language);
  }

  hasText(): boolean {
    return this.articleText.trim().length > 0;
  }

  hasUrl(): boolean {
    return this.articleUrl.trim().length > 0;
  }

  reviewText() {
    if (!this.hasText()) {
      return;
    }

    this.reviewing.set(true);
    this.reviewResult.set('');

    setTimeout(() => {
      this.reviewing.set(false);
      this.reviewResult.set(this.t().sampleResult);
    }, 800);
  }

  reviewUrl() {
    if (!this.hasUrl()) {
      return;
    }

    this.reviewing.set(true);
    this.reviewResult.set('');

    setTimeout(() => {
      this.reviewing.set(false);
      this.reviewResult.set(this.t().sampleResult);
    }, 800);
  }
}
