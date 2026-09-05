import { Component, signal, afterNextRender } from '@angular/core';

import { FormsModule } from '@angular/forms';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';

type Language = 'en' | 'ms' | 'zh';

type ArticleFilter = 'Latest' | 'This week' | 'Interest' | 'Following';

interface Article {
  id: number;
  title: string;
  category: string;
  description: string;
  thumbnail: string;
  filters: string[];
  featured: boolean;
  author: string;
}

@Component({
  selector: 'app-homepage',
  standalone: true,

  imports: [
    FormsModule,
    HlmButtonImports,
    HlmDropdownMenuImports,
    HlmInputImports,
    HlmTextareaImports,
  ],

  templateUrl: './homepage.html',
  styleUrl: './homepage.css',
})
export class Homepage {
  // -----------------------------
  // LANGUAGE
  // -----------------------------

  language = signal<Language>('en');

  // -----------------------------
  // REVIEW INPUT
  // -----------------------------

  articleText: string = '';
  articleUrl: string = '';

  reviewing = signal<boolean>(false);
  reviewResult = signal<string>('');

  // -----------------------------
  // ARTICLE FILTER
  // -----------------------------

  activeFilter = signal<ArticleFilter>('Latest');

  // -----------------------------
  // ARTICLES
  // -----------------------------

  articles = signal<Article[]>([]);

  // -----------------------------
  // TRANSLATIONS
  // -----------------------------

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
        'Kirkify helps you review articles for clarity, credibility, bias, and important claims.',

      textLabel: 'Paste your article',

      textPlaceholder: 'Paste the article text you want Kirkify to review...',

      urlLabel: 'Or review an article URL',

      urlPlaceholder: 'https://example.com/article',

      review: 'Review',

      textHint: 'Paste the article text here.',

      urlHint: 'Enter the URL of the article you want to review.',

      resultTitle: 'Review Result',

      resultPlaceholder: 'Your article review will appear here.',

      reviewing: 'Reviewing...',

      articlesTitle: 'Explore articles',

      articlesDescription: 'Discover articles worth reading, questioning and thinking about.',

      latest: 'Latest',

      thisWeek: 'This week',

      interest: 'Interest',

      following: 'Following',

      featured: 'Featured',

      readArticle: 'Read article',

      sampleResult:
        'This is a sample review. Your article has been submitted successfully. Kirkify can analyze its clarity, claims, potential bias, and credibility.',
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
        'Kirkify membantu anda menyemak artikel dari segi kejelasan, kredibiliti, bias dan dakwaan penting.',

      textLabel: 'Tampal artikel anda',

      textPlaceholder: 'Tampal teks artikel yang ingin anda semak...',

      urlLabel: 'Atau semak URL artikel',

      urlPlaceholder: 'https://example.com/article',

      review: 'Semak',

      textHint: 'Tampal teks artikel di sini.',

      urlHint: 'Masukkan URL artikel yang ingin anda semak.',

      resultTitle: 'Keputusan Semakan',

      resultPlaceholder: 'Semakan artikel anda akan muncul di sini.',

      reviewing: 'Sedang menyemak...',

      articlesTitle: 'Terokai artikel',

      articlesDescription: 'Temui artikel yang menarik untuk dibaca, dipersoalkan dan difikirkan.',

      latest: 'Terkini',

      thisWeek: 'Minggu ini',

      interest: 'Minat',

      following: 'Mengikuti',

      featured: 'Pilihan',

      readArticle: 'Baca artikel',

      sampleResult: 'Ini ialah contoh semakan. Artikel anda telah berjaya dihantar.',
    },

    zh: {
      home: '首页',
      howItWorks: '使用方法',
      about: '关于',
      language: '语言',

      badge: 'AI 智能文章审查',

      title: '了解你的文章。',
      titleHighlight: '在相信它之前。',

      description: 'Kirkify 帮助你检查文章的清晰度、可信度、偏见以及重要论点。',

      textLabel: '粘贴你的文章',

      textPlaceholder: '粘贴你想让 Kirkify 审查的文章内容...',

      urlLabel: '或者输入文章网址',

      urlPlaceholder: 'https://example.com/article',

      review: '审查',

      textHint: '在这里粘贴文章内容。',

      urlHint: '输入你想审查的文章网址。',

      resultTitle: '审查结果',

      resultPlaceholder: '你的文章审查结果将在这里显示。',

      reviewing: '正在审查...',

      articlesTitle: '探索文章',

      articlesDescription: '发现值得阅读、质疑和思考的文章。',

      latest: '最新',

      thisWeek: '本周',

      interest: '兴趣',

      following: '关注',

      featured: '精选',

      readArticle: '阅读文章',

      sampleResult: '这是一个示例审查结果。你的文章已经成功提交。',
    },
  };

  // -----------------------------
  // CONSTRUCTOR
  // -----------------------------

  constructor() {
    afterNextRender(() => {
      this.loadArticles();
    });
  }

  // -----------------------------
  // TRANSLATION
  // -----------------------------

  t() {
    return this.translations[this.language()];
  }

  // -----------------------------
  // LANGUAGE
  // -----------------------------

  setLanguage(language: Language): void {
    this.language.set(language);
  }

  // -----------------------------
  // ARTICLE FILTER
  // -----------------------------

  setFilter(filter: ArticleFilter): void {
    this.activeFilter.set(filter);
  }

  filteredArticles(): Article[] {
    const filterMap: Record<ArticleFilter, string> = {
      Latest: 'latest',

      'This week': 'this-week',

      Interest: 'interest',

      Following: 'following',
    };

    const currentFilter: string = filterMap[this.activeFilter()];

    return this.articles().filter((article: Article) => article.filters.includes(currentFilter));
  }

  // -----------------------------
  // ARTICLE LOADING
  // -----------------------------

  async loadArticles(): Promise<void> {
    try {
      const response: Response = await fetch('/articles.txt');

      if (!response.ok) {
        throw new Error(`Failed to load articles.txt: ${response.status}`);
      }

      const text: string = await response.text();

      const articles: Article[] = text
        .split(/\r?\n/)
        .filter((line: string) => line.trim().length > 0)
        .map((line: string) => this.parseArticle(line));

      this.articles.set(articles);

      console.log('Articles loaded:', articles);
    } catch (error) {
      console.error('Could not load articles.txt:', error);
    }
  }

  parseArticle(line: string): Article {
    const parts: string[] = line.split('|');

    return {
      id: Number(parts[0]),

      title: parts[1] ?? '',

      category: parts[2] ?? '',

      description: parts[3] ?? '',

      thumbnail: parts[4] ?? '',

      filters: (parts[5] ?? '').split(',').map((filter: string) => filter.trim()),

      featured: parts[6]?.trim() === 'true',

      author: parts[7] ?? '',
    };
  }

  // -----------------------------
  // REVIEW
  // -----------------------------

  hasText(): boolean {
    return this.articleText.trim().length > 0;
  }

  hasUrl(): boolean {
    return this.articleUrl.trim().length > 0;
  }

  reviewText(): void {
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

  reviewUrl(): void {
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
