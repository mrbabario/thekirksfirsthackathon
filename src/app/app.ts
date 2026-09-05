import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Homepage } from './pages/homepage/homepage';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Homepage],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('thekirksfirsthackathon');
}
