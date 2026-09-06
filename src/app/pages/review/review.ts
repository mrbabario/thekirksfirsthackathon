import {
  Component,
  OnDestroy,
  afterNextRender,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmCardImports } from '@spartan-ng/helm/card';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';

import { FactCheckerService } from '../../core/services/fact-checker';
import {
  ArticleResult,
  Reference,
  Verdict,
} from '../../core/models/result';

interface PipelineStage {
  label: string;
  detail: string;
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
    HlmDropdownMenuImports,
    DecimalPipe,
  ],
  templateUrl: './review.html',
  styleUrl: './review.css',
})
export class ReviewPage implements OnDestroy {
  articleText = '';
  articleUrl = '';

  analyzing = signal(false);
  hasResult = signal(false);

  review = signal<ArticleResult | null>(null);
  errorMessage = signal<string | null>(null);

  expandedClaims = signal<number[]>([]);
  expandedReferences = signal<string[]>([]);

  currentStage = signal(0);
  terminalStarted = signal(false);

  terminalLines = signal<string[]>([]);

  readonly pipelineStages: PipelineStage[] = [
    {
      label: 'PARSING ARTICLE',
      detail: 'Cleaning and normalising article content...',
    },
    {
      label: 'DETECTING LANGUAGE',
      detail: 'Identifying the article language...',
    },
    {
      label: 'EXTRACTING CLAIMS',
      detail:
        'Gemma is breaking the article into verifiable claims...',
    },
    {
      label: 'GENERATING QUERIES',
      detail:
        'Building targeted biomedical search queries...',
    },
    {
      label: 'SEARCHING PUBMED',
      detail:
        'Retrieving relevant scientific literature...',
    },
    {
      label: 'RANKING EVIDENCE',
      detail:
        'Comparing claims against candidate references...',
    },
    {
      label: 'RERANKING SOURCES',
      detail:
        'Applying cross-encoder relevance scoring...',
    },
    {
      label: 'ANALYSING CLAIMS',
      detail:
        'Gemma is comparing claims with the evidence...',
    },
    {
      label: 'VALIDATING REFERENCES',
      detail:
        'Checking citation consistency and source IDs...',
    },
    {
      label: 'FINALISING REVIEW',
      detail:
        'Preparing the evidence-backed result...',
    },
  ];

  private readonly maxTerminalLines = 7;

  private stageTimer?: ReturnType<typeof setInterval>;

  constructor(
    private factChecker: FactCheckerService,
  ) {
    const state = history.state as {
      articleText?: string;
      articleUrl?: string;
    };

    this.articleText = state?.articleText ?? '';
    this.articleUrl = state?.articleUrl ?? '';

    afterNextRender(() => {
      if (
        this.articleText.trim() ||
        this.articleUrl.trim()
      ) {
        this.runAnalysis();
      }
    });
  }

  ngOnDestroy(): void {
    this.stopStageAnimation();
  }

  totalClaims(): number {
    return this.review()?.claims.length ?? 0;
  }

  allReferences(): Reference[] {
    const result = this.review();

    if (!result) {
      return [];
    }

    const map = new Map<number, Reference>();

    for (const claim of result.claims) {
      for (const reference of claim.references) {
        map.set(reference.number, reference);
      }
    }

    return Array.from(map.values());
  }

  countVerdict(verdict: Verdict): number {
    return (
      this.review()?.claims.filter(
        claim => claim.verdict === verdict,
      ).length ?? 0
    );
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
        return 'Supported';

      case 'MIXED':
        return 'Mixed';

      case 'INSUFFICIENT':
        return 'Insufficient evidence';

      case 'CONTRADICTED':
        return 'Refuted';
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

      case 'CONTRADICTED':
        return '×';
    }
  }

  runAnalysis(): void {
    const text = this.articleText.trim();
    const url = this.articleUrl.trim();

    if (!text && !url) {
      return;
    }

    this.errorMessage.set(null);

    this.analyzing.set(true);
    this.hasResult.set(false);
    this.review.set(null);

    this.expandedClaims.set([]);
    this.expandedReferences.set([]);

    this.currentStage.set(0);
    this.terminalStarted.set(true);

    this.startStageAnimation();

    const request = {
      text: text || undefined,
      url: url || undefined,
    };

    this.factChecker.checkArticle(request).subscribe({
      next: (result) => {
        this.stopStageAnimation();

        const finalStage =
          this.pipelineStages[
            this.pipelineStages.length - 1
          ];

        this.addTerminalLine(
          `[DONE]    ${finalStage.label}`,
        );

        this.addTerminalLine(
          '> Evidence-backed review complete.',
        );

        this.currentStage.set(
          this.pipelineStages.length - 1,
        );

        this.review.set(result);
        this.analyzing.set(false);
        this.hasResult.set(true);
      },

      error: (error) => {
        console.error('Fact check failed:', error);

        this.stopStageAnimation();

        this.addTerminalLine(
          '> ERROR: Fact-check request failed.',
        );

        this.analyzing.set(false);
        this.hasResult.set(false);

        this.errorMessage.set(
          'The article could not be reviewed. Please check the URL and try again.',
        );
      },
    });
  }

  analyzeReference(reference: Reference): void {
    const url =
      `https://pubmed.ncbi.nlm.nih.gov/${reference.pmid}/`;

    this.stopStageAnimation();

    this.articleText = '';
    this.articleUrl = url;

    this.review.set(null);
    this.hasResult.set(false);
    this.analyzing.set(false);

    this.errorMessage.set(null);

    this.expandedClaims.set([]);
    this.expandedReferences.set([]);

    this.currentStage.set(0);
    this.terminalStarted.set(false);
    this.terminalLines.set([]);

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  startNewReview(): void {
    this.stopStageAnimation();

    this.analyzing.set(false);
    this.hasResult.set(false);
    this.review.set(null);

    this.errorMessage.set(null);

    this.articleText = '';
    this.articleUrl = '';

    this.expandedClaims.set([]);
    this.expandedReferences.set([]);

    this.currentStage.set(0);
    this.terminalStarted.set(false);
    this.terminalLines.set([]);

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  private startStageAnimation(): void {
    this.stopStageAnimation();

    this.terminalLines.set([
      '$ drkirk review --article',
      '> Initialising evidence pipeline...',
    ]);

    this.currentStage.set(0);

    this.addTerminalLine(
      `[RUNNING] ${this.pipelineStages[0].label}`,
    );

    this.stageTimer = setInterval(() => {
      const nextStage = this.currentStage() + 1;

      if (
        nextStage >= this.pipelineStages.length
      ) {
        return;
      }

      const previousStage =
        this.pipelineStages[this.currentStage()];

      this.addTerminalLine(
        `[DONE]    ${previousStage.label}`,
      );

      this.currentStage.set(nextStage);

      const nextStageDefinition =
        this.pipelineStages[nextStage];

      this.addTerminalLine(
        `[RUNNING] ${nextStageDefinition.label}`,
      );
    }, 1800);
  }

  private addTerminalLine(line: string): void {
    const lines = [
      ...this.terminalLines(),
      line,
    ];

    if (lines.length > this.maxTerminalLines) {
      lines.splice(
        0,
        lines.length - this.maxTerminalLines,
      );
    }

    this.terminalLines.set(lines);
  }

  private stopStageAnimation(): void {
    if (this.stageTimer) {
      clearInterval(this.stageTimer);
      this.stageTimer = undefined;
    }
  }
}
