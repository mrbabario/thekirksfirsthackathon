export interface Claim {
  text: string;
  subject: string;
  predicate: string;
  object: string;
  entities: string[];
  language: string;
}

export type Verdict =
  | 'SUPPORTED'
  | 'CONTRADICTED'
  | 'MIXED'
  | 'INSUFFICIENT';

export interface ExplanationPart {
  text: string;
  references: number[];
}

export interface Reference {
  number: number;
  pmid: string;
  title: string;
  abstract: string;
  journal: string;
  year: number | null;
}

export interface ClaimResult {
  claim: Claim;
  verdict: Verdict;
  explanation: ExplanationPart[];
  references: Reference[];
}

export interface ArticleResult {
  article_hash: string;
  language: string;
  claims: ClaimResult[];
}
