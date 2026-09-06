import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';
import { DecimalPipe } from '@angular/common';

type Language = 'en' | 'ms' | 'zh';
type Verdict = 'SUPPORTED' | 'MIXED' | 'INSUFFICIENT' | 'REFUTED';

interface Claim {
  text: string;
  subject: string;
  predicate: string;
  object: string;
  entities: string[];
  language: string;
}

interface Explanation {
  text: string;
  references: number[];
}

interface Reference {
  number: number;
  pmid: string;
  title: string;
  abstract: string;
  journal: string;
  year: number;
}

interface ClaimResult {
  claim: Claim;
  verdict: Verdict;
  explanation: Explanation[];
  references: Reference[];
}

interface ReviewResult {
  article_hash: string;
  language: string;
  claims: ClaimResult[];
}

interface Translation {
  home: string;
  howItWorks: string;
  articles: string;
  forum: string;
  signIn: string;
  language: string;

  badge: string;
  title: string;
  subtitle: string;

  overall: string;
  claimsAnalyzed: string;
  sourcesFound: string;
  supported: string;
  mixed: string;
  insufficient: string;
  refuted: string;

  claimAnalysis: string;
  evidence: string;
  references: string;
  explanation: string;
  source: string;
  openReference: string;
  hideReference: string;

  analyzeAnother: string;
  articleInput: string;
  articleInputPlaceholder: string;
  articleUrl: string;
  articleUrlPlaceholder: string;
  analyze: string;
  analyzing: string;
}

@Component({
  selector: 'app-review',
  standalone: true,
  imports: [
    RouterLink,
    FormsModule,
    HlmButtonImports,
    HlmCardImports,
    HlmInputImports,
    HlmTextareaImports,
    DecimalPipe,
  ],
  templateUrl: './review.html',
  styleUrl: './review.css',
})
export class ReviewPage {
  language = signal<Language>('en');

  articleText = '';
  articleUrl = '';

  analyzing = signal(false);
  hasResult = signal(true);

  expandedClaims = signal<number[]>([]);
  expandedReferences = signal<string[]>([]);

  review = signal<ReviewResult>(this.mockReview());

  translations: Record<Language, Translation> = {
    en: {
      home: 'Home',
      howItWorks: 'How It Works',
      articles: 'Explore Articles',
      forum: 'Forum',
      signIn: 'Sign in',
      language: 'English',

      badge: 'AI Article Review',
      title: 'Dr.Kirk review',
      subtitle:
        'A claim-by-claim breakdown of the information found in this article.',

      overall: 'Review overview',
      claimsAnalyzed: 'Claims analyzed',
      sourcesFound: 'Sources found',
      supported: 'Supported',
      mixed: 'Mixed',
      insufficient: 'Insufficient evidence',
      refuted: 'Refuted',

      claimAnalysis: 'Claim analysis',
      evidence: 'Evidence',
      references: 'References',
      explanation: 'Why Dr.Kirk reached this verdict',
      source: 'Source',
      openReference: 'Show source',
      hideReference: 'Hide source',

      analyzeAnother: 'Analyze another article',
      articleInput: 'Article text',
      articleInputPlaceholder:
        'Paste an article for Dr.Kirk to analyze...',
      articleUrl: 'Article URL',
      articleUrlPlaceholder: 'https://example.com/article',
      analyze: 'Analyze',
      analyzing: 'Analyzing...',
    },

    ms: {
      home: 'Laman Utama',
      howItWorks: 'Cara Ia Berfungsi',
      articles: 'Terokai Artikel',
      forum: 'Forum',
      signIn: 'Log masuk',
      language: 'Bahasa Melayu',

      badge: 'Semakan Artikel AI',
      title: 'Semakan Dr.Kirk',
      subtitle:
        'Pecahan dakwaan demi dakwaan berdasarkan maklumat yang terdapat dalam artikel.',

      overall: 'Ringkasan semakan',
      claimsAnalyzed: 'Dakwaan dianalisis',
      sourcesFound: 'Sumber ditemui',
      supported: 'Disokong',
      mixed: 'Bercampur',
      insufficient: 'Bukti tidak mencukupi',
      refuted: 'Disangkal',

      claimAnalysis: 'Analisis dakwaan',
      evidence: 'Bukti',
      references: 'Rujukan',
      explanation: 'Mengapa Dr.Kirk memberikan keputusan ini',
      source: 'Sumber',
      openReference: 'Lihat sumber',
      hideReference: 'Sembunyikan sumber',

      analyzeAnother: 'Analisis artikel lain',
      articleInput: 'Teks artikel',
      articleInputPlaceholder:
        'Tampal artikel untuk dianalisis oleh Dr.Kirk...',
      articleUrl: 'URL artikel',
      articleUrlPlaceholder: 'https://example.com/article',
      analyze: 'Analisis',
      analyzing: 'Sedang menganalisis...',
    },

    zh: {
      home: '首页',
      howItWorks: '使用方法',
      articles: '探索文章',
      forum: '论坛',
      signIn: '登录',
      language: '中文',

      badge: 'AI 文章审查',
      title: 'Dr.Kirk 审查结果',
      subtitle:
        '根据文章中的信息，对重要论点进行逐条分析。',

      overall: '审查概览',
      claimsAnalyzed: '已分析论点',
      sourcesFound: '找到的来源',
      supported: '有支持',
      mixed: '混合',
      insufficient: '证据不足',
      refuted: '已反驳',

      claimAnalysis: '论点分析',
      evidence: '证据',
      references: '参考文献',
      explanation: '为什么 Dr.Kirk 得出这个结论',
      source: '来源',
      openReference: '查看来源',
      hideReference: '隐藏来源',

      analyzeAnother: '分析另一篇文章',
      articleInput: '文章内容',
      articleInputPlaceholder:
        '粘贴需要 Dr.Kirk 分析的文章...',
      articleUrl: '文章网址',
      articleUrlPlaceholder: 'https://example.com/article',
      analyze: '分析',
      analyzing: '正在分析...',
    },
  };

  constructor() {
    const navigationState = history.state as {
      articleText?: string;
      articleUrl?: string;
    };

    if (navigationState?.articleText) {
      this.articleText = navigationState.articleText;
    }

    if (navigationState?.articleUrl) {
      this.articleUrl = navigationState.articleUrl;
    }

    /*
     * Later:
     *
     * this.review.set(await this.reviewService.review(...));
     *
     * For now the page displays your supplied JSON structure.
     */
  }

  t(): Translation {
    return this.translations[this.language()];
  }

  setLanguage(language: Language): void {
    this.language.set(language);
  }

  totalClaims(): number {
    return this.review().claims.length;
  }

  allReferences(): Reference[] {
    const map = new Map<number, Reference>();

    for (const claim of this.review().claims) {
      for (const reference of claim.references) {
        map.set(reference.number, reference);
      }
    }

    return Array.from(map.values());
  }

  countVerdict(verdict: Verdict): number {
    return this.review().claims.filter(
      claim => claim.verdict === verdict,
    ).length;
  }

  toggleClaim(index: number): void {
    const expanded = [...this.expandedClaims()];

    const existingIndex = expanded.indexOf(index);

    if (existingIndex >= 0) {
      expanded.splice(existingIndex, 1);
    } else {
      expanded.push(index);
    }

    this.expandedClaims.set(expanded);
  }

  isClaimExpanded(index: number): boolean {
    return this.expandedClaims().includes(index);
  }

  toggleReference(
    claimIndex: number,
    referenceNumber: number,
  ): void {
    const key = `${claimIndex}-${referenceNumber}`;
    const expanded = [...this.expandedReferences()];

    const existingIndex = expanded.indexOf(key);

    if (existingIndex >= 0) {
      expanded.splice(existingIndex, 1);
    } else {
      expanded.push(key);
    }

    this.expandedReferences.set(expanded);
  }

  isReferenceExpanded(
    claimIndex: number,
    referenceNumber: number,
  ): boolean {
    return this.expandedReferences().includes(
      `${claimIndex}-${referenceNumber}`,
    );
  }

  verdictLabel(verdict: Verdict): string {
    switch (verdict) {
      case 'SUPPORTED':
        return this.t().supported;

      case 'MIXED':
        return this.t().mixed;

      case 'INSUFFICIENT':
        return this.t().insufficient;

      case 'REFUTED':
        return this.t().refuted;
    }
  }

  verdictIcon(verdict: Verdict): string {
    switch (verdict) {
      case 'SUPPORTED':
        return '✓';

      case 'MIXED':
        return '◐';

      case 'INSUFFICIENT':
        return '?';

      case 'REFUTED':
        return '×';
    }
  }

  startNewReview(): void {
    this.hasResult.set(false);
    this.articleText = '';
    this.articleUrl = '';
  }

  runAnalysis(): void {
    if (!this.articleText.trim() && !this.articleUrl.trim()) {
      return;
    }

    this.analyzing.set(true);
    this.hasResult.set(false);

    setTimeout(() => {
      this.analyzing.set(false);
      this.hasResult.set(true);
    }, 1200);
  }

  mockReview(): ReviewResult {
    return {
      article_hash:
        '0f88dae95e1f3af3777e5d26c085b7c2fb196e66cb08c6827bb96c878b00f6af',

      language: 'en',

      claims: [
        {
          claim: {
            text:
              'COVID-19 vaccines are causing cancer rates to skyrocket',
            subject: 'COVID-19 vaccines',
            predicate: 'causing',
            object: 'cancer rates to skyrocket',
            entities: [
              'COVID-19 vaccines',
              'cancer rates',
            ],
            language: 'en',
          },

          verdict: 'INSUFFICIENT',

          explanation: [
            {
              text:
                'No relevant biomedical references were found.',
              references: [],
            },
          ],

          references: [],
        },

        {
          claim: {
            text:
              'mRNA COVID-19 vaccines are meant to kill people',
            subject: 'mRNA COVID-19 vaccines',
            predicate: 'are meant to',
            object: 'kill people',
            entities: ['mRNA COVID-19 vaccines'],
            language: 'en',
          },

          verdict: 'MIXED',

          explanation: [
            {
              text:
                'The claim is not directly supported by the provided references. Some references discuss potential adverse immune responses and serious adverse events following vaccination, but these do not establish that vaccines are intended to kill people.',
              references: [2, 3, 4, 5],
            },
          ],

          references: [
            {
              number: 2,
              pmid: '36045681',
              title:
                'Four cases of cytokine storm after COVID-19 vaccination: Case report.',
              abstract:
                'The study presents four cases of death following vaccination and investigates possible immune dysregulation following vaccination.',
              journal: 'Frontiers in Immunology',
              year: 2022,
            },

            {
              number: 3,
              pmid: '37660743',
              title:
                'Similarities and differences between myocarditis following COVID-19 mRNA vaccine and multiple inflammatory syndrome with cardiac involvement in children.',
              abstract:
                'The study discusses cardiac adverse events following COVID-19 immunization and inflammatory profiles in affected patients.',
              journal: 'Clinical Immunology',
              year: 2023,
            },

            {
              number: 4,
              pmid: '41683812',
              title:
                'Interleukins in COVID-19 and SARS-CoV-2 Variants: Immunopathogenesis, Therapeutic Perspectives and Vaccine-Induced Immune Responses.',
              abstract:
                'A review discussing interleukins, immune responses, and inflammatory mechanisms associated with COVID-19 and vaccination.',
              journal:
                'International Journal of Molecular Sciences',
              year: 2026,
            },

            {
              number: 5,
              pmid: '42421498',
              title:
                'Xenosialylation as immunological chimerism: a host-centered unifying model for viral and post-vaccination immune complications.',
              abstract:
                'A hypothesis-driven model proposing potential mechanisms for immune dysregulation following viral infection and vaccination.',
              journal: 'European Cytokine Network',
              year: 2026,
            },
          ],
        },

        {
          claim: {
            text:
              'There is a 163 percent increase in deaths year over year',
            subject: 'deaths',
            predicate: 'increase',
            object: '163 percent year over year',
            entities: ['deaths'],
            language: 'en',
          },

          verdict: 'INSUFFICIENT',

          explanation: [
            {
              text:
                'The provided references do not directly support a 163 percent year-over-year increase in deaths. Some references describe mortality trends in specific diseases or populations, but these cannot be used to establish the broader claim.',
              references: [1, 2, 3, 4, 5],
            },
          ],

          references: [
            {
              number: 1,
              pmid: '40994710',
              title:
                'Global, regional, and national burden of intracerebral hemorrhage and attributable risk factors in youths and young adults, 1990-2021.',
              abstract:
                'This study examines global trends in intracerebral hemorrhage among youths and young adults using Global Burden of Disease data.',
              journal: 'Frontiers in Neurology',
              year: 2025,
            },

            {
              number: 2,
              pmid: '41293343',
              title:
                'A Retrospective Study on Temporal Trends in Mortality Related to Atrial Fibrillation and Chronic Obstructive Pulmonary Disease.',
              abstract:
                'A retrospective analysis of mortality trends involving atrial fibrillation and COPD in adults in the United States.',
              journal: 'Cureus',
              year: 2025,
            },

            {
              number: 3,
              pmid: '35812615',
              title:
                'Temporal Trends for Patients Hospitalized With Atrial Fibrillation in the United States.',
              abstract:
                'Analysis of hospitalization trends and mortality outcomes among patients hospitalized with atrial fibrillation.',
              journal: 'Cureus',
              year: 2022,
            },

            {
              number: 4,
              pmid: '33526723',
              title:
                'Temporal Trends of Cervical Cancer Mortality in Georgia, 2011-2018.',
              abstract:
                'Study of cervical cancer mortality rates and temporal trends in Georgia.',
              journal: 'Georgian Medical News',
              year: 2020,
            },

            {
              number: 5,
              pmid: '39618616',
              title:
                'Trends in the Incidence of Brain Cancer: An Observational Study.',
              abstract:
                'An observational analysis of brain cancer incidence trends using CDC WONDER data.',
              journal: 'Cureus',
              year: 2024,
            },
          ],
        },
      ],
    };
  }
}
