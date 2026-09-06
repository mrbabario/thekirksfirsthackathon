import { Component, signal, afterNextRender } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink, Router} from '@angular/router';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';

import { AuthService } from '../../core/services/auth';

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

interface Translation {
  home: string;
  howItWorks: string;
  articlesTitle: string;
  articlesDescription: string;
  about: string;
  language: string;

  badge: string;
  title: string;
  titleHighlight: string;
  description: string;

  textLabel: string;
  textHint: string;
  textPlaceholder: string;

  urlLabel: string;
  urlHint: string;
  urlPlaceholder: string;

  review: string;
  reviewing: string;

  resultTitle: string;
  resultPlaceholder: string;
  sampleResult: string;

  latest: string;
  thisWeek: string;
  interest: string;
  following: string;

  featured: string;
  readArticle: string;
}

@Component({
  selector: 'app-homepage',
  standalone: true,

  imports: [
    RouterLink,
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
  // TYPING ANIMATION
  // -----------------------------

  displayedTitle = signal('');
  displayedTitleHighlight = signal('');

  private typingRunId = 0;

  // -----------------------------
  // REVIEW INPUT
  // -----------------------------

  articleText = '';
  articleUrl = '';

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

  translations: Record<Language, Translation> = {
    // ==========================================
    // ENGLISH
    // ==========================================
    en: {
      home: 'Home',
      howItWorks: 'How It Works',
      articlesTitle: 'Explore articles',
      articlesDescription:
        'Discover articles worth reading, questioning and thinking about.',
      about: 'About',
      language: 'Language',

      badge: 'AI-Powered Article Review',

      title: 'Before you trust an article.',
      titleHighlight: 'Let Dr.Kirk verify it.',

      description:
        'Dr.Kirk helps you review articles for clarity, credibility, bias, and important claims.',

      textLabel: 'Paste your article',
      textHint: 'Paste the article text here.',
      textPlaceholder:
        'Paste the article text you want Dr.Kirk to review...',

      urlLabel: 'Or review an article URL',
      urlHint: 'Enter the URL of the article you want to review.',
      urlPlaceholder: 'https://example.com/article',

      review: 'Review',
      reviewing: 'Reviewing...',

      resultTitle: 'Review Result',
      resultPlaceholder: 'Your article review will appear here.',

      sampleResult:
        'This is a sample review. Your article has been submitted successfully. Dr.Kirk can analyze its clarity, claims, potential bias, and credibility.',

      latest: 'Latest',
      thisWeek: 'This week',
      interest: 'Interest',
      following: 'Following',

      featured: 'Featured',
      readArticle: 'Read article',
    },

    // ==========================================
    // BAHASA MELAYU
    // ==========================================
    ms: {
      home: 'Laman Utama',
      howItWorks: 'Cara Ia Berfungsi',
      articlesTitle: 'Terokai artikel',
      articlesDescription:
        'Temui artikel yang berbaloi untuk dibaca, dipersoalkan dan difikirkan.',
      about: 'Tentang',
      language: 'Bahasa',

      badge: 'Semakan Artikel Berkuasa AI',

      title: 'Sebelum anda mempercayai artikel tersebut.',
      titleHighlight: 'Biar Dr.Kirk mengesahkannya.',

      description:
        'Dr.Kirk membantu anda menyemak artikel dari segi kejelasan, kredibiliti, bias dan dakwaan penting.',

      textLabel: 'Tampal artikel anda',
      textHint: 'Tampal teks artikel di sini.',
      textPlaceholder:
        'Tampal teks artikel yang ingin anda semak...',

      urlLabel: 'Atau semak URL artikel',
      urlHint: 'Masukkan URL artikel yang ingin anda semak.',
      urlPlaceholder: 'https://example.com/article',

      review: 'Semak',
      reviewing: 'Sedang menyemak...',

      resultTitle: 'Keputusan Semakan',
      resultPlaceholder: 'Semakan artikel anda akan muncul di sini.',

      sampleResult:
        'Ini ialah contoh semakan. Artikel anda telah berjaya dihantar. Dr.Kirk boleh menganalisis kejelasan, dakwaan, kemungkinan bias dan kredibiliti.',

      latest: 'Terkini',
      thisWeek: 'Minggu ini',
      interest: 'Minat',
      following: 'Mengikuti',

      featured: 'Pilihan',
      readArticle: 'Baca artikel',
    },

    // ==========================================
    // CHINESE
    // ==========================================
    zh: {
      home: '首页',
      howItWorks: '使用方法',
      articlesTitle: '探索文章',
      articlesDescription: '发现值得阅读、质疑和思考的文章。',
      about: '关于',
      language: '语言',

      badge: 'AI 智能文章审查',

      title: '在相信文章前。',
      titleHighlight: '让 Dr.Kirk 验证您的文章。',

      description:
        'Dr.Kirk 帮助您检查文章的清晰度、可信度、偏见以及重要论点。',

      textLabel: '粘贴您的文章',
      textHint: '在这里粘贴文章内容。',
      textPlaceholder:
        '粘贴您想让 Dr.Kirk 审查的文章内容...',

      urlLabel: '或者输入文章网址',
      urlHint: '输入您想审查的文章网址。',
      urlPlaceholder: 'https://example.com/article',

      review: '审查',
      reviewing: '正在审查...',

      resultTitle: '审查结果',
      resultPlaceholder: '您的文章审查结果将在这里显示。',

      sampleResult:
        '这是一个示例审查结果。您的文章已经成功提交。Dr.Kirk 可以分析文章的清晰度、论点、潜在偏见和可信度。',

      latest: '最新',
      thisWeek: '本周',
      interest: '兴趣',
      following: '关注',

      featured: '精选',
      readArticle: '阅读文章',
    },
  };

  // -----------------------------
  // CONSTRUCTOR
  // -----------------------------

  constructor(
    public authService: AuthService,
    private router: Router,
  ) {
    afterNextRender(() => {
      this.startTypingAnimation();
      this.loadArticles();
    });
  }

  logout() {
  this.authService.logout();

  this.router.navigate(['/']);
}

  // -----------------------------
  // TRANSLATION
  // -----------------------------

  t(): Translation {
    return this.translations[this.language()];
  }

  // -----------------------------
  // LANGUAGE
  // -----------------------------

  setLanguage(language: Language): void {
    this.language.set(language);

    this.startTypingAnimation();
  }

  // -----------------------------
  // TYPING ANIMATION
  // -----------------------------

  private startTypingAnimation(): void {
    const currentRun = ++this.typingRunId;

    this.displayedTitle.set('');
    this.displayedTitleHighlight.set('');

    const title = this.t().title;
    const titleHighlight = this.t().titleHighlight;

    this.typeText(
      title,
      this.displayedTitle,
      currentRun,
      36
    ).then(() => {
      if (currentRun !== this.typingRunId) {
        return;
      }

      return this.typeText(
        titleHighlight,
        this.displayedTitleHighlight,
        currentRun,
        36
      );
    });
  }

  private typeText(
    text: string,
    target: ReturnType<typeof signal<string>>,
    runId: number,
    speed: number
  ): Promise<void> {
    return new Promise((resolve) => {
      let index = 0;

      const typeNextCharacter = () => {
        if (runId !== this.typingRunId) {
          resolve();
          return;
        }

        if (index >= text.length) {
          resolve();
          return;
        }

        target.set(text.slice(0, index + 1));
        index++;

        setTimeout(typeNextCharacter, speed);
      };

      typeNextCharacter();
    });
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

    const currentFilter = filterMap[this.activeFilter()];

    return this.articles().filter(
      (article: Article) =>
        article.filters.includes(currentFilter)
    );
  }

  // -----------------------------
  // ARTICLE LOADING
  // -----------------------------

  async loadArticles(): Promise<void> {
    try {
      const response: Response = await fetch('/articles.txt');

      if (!response.ok) {
        throw new Error(
          `Failed to load articles.txt: ${response.status}`
        );
      }

      const text: string = await response.text();

      const articles: Article[] = text
        .split(/\r?\n/)
        .filter(
          (line: string) =>
            line.trim().length > 0
        )
        .map(
          (line: string) =>
            this.parseArticle(line)
        );

      this.articles.set(articles);

      console.log('Articles loaded:', articles);
    } catch (error) {
      console.error(
        'Could not load articles.txt:',
        error
      );
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
      filters: (parts[5] ?? '')
        .split(',')
        .map(
          (filter: string) =>
            filter.trim()
        ),
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

    this.router.navigate(['/review'], {
      state: {
        articleText: this.articleText.trim(),
      },
    });
  }

  reviewUrl(): void {
    if (!this.hasUrl()) {
      return;
    }

    this.router.navigate(['/review'], {
      state: {
        articleUrl: this.articleUrl.trim(),
      },
    });
  }
}
