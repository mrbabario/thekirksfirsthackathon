import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import {
  ArticleResult,
} from '../models/result';

export interface CheckRequest {
  text?: string;
  url?: string;
}

@Injectable({
  providedIn: 'root',
})
export class FactCheckerService {

  private http = inject(HttpClient);

  private readonly apiUrl =
    'http://localhost:8000/api';

  checkArticle(
    request: CheckRequest
  ) {
    return this.http.post<ArticleResult>(
      `${this.apiUrl}/check`,
      request
    );
  }
}
