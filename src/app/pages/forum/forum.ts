import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmDropdownMenuImports } from '@spartan-ng/helm/dropdown-menu';

interface ForumPost {
  id: number;
  title: string;
  category: string;
  description: string;
  author: string;
  replies: number;
  views: number;
  time: string;
  tag: string;
  pinned?: boolean;
}

@Component({
  selector: 'app-forum',
  standalone: true,

  imports: [RouterLink, HlmButtonImports, HlmDropdownMenuImports],

  templateUrl: './forum.html',
  styleUrl: './forum.css',
})
export class Forum {
  language = 'Language';

  setLanguage(language: 'en' | 'ms' | 'zh'): void {
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

  categories = [
    {
      name: 'General Discussion',
      description: 'Talk about articles, ideas, and anything related to critical thinking.',
      posts: 128,
      icon: '💬',
    },
    {
      name: 'Fact Checking',
      description: 'Discuss claims, sources, evidence, and questionable information.',
      posts: 94,
      icon: '🔎',
    },
    {
      name: 'Media & News',
      description: 'Share and discuss current news, media coverage, and reporting.',
      posts: 76,
      icon: '📰',
    },
    {
      name: 'Help & Feedback',
      description: 'Ask questions or share suggestions about Dr.Kirk.',
      posts: 41,
      icon: '💡',
    },
  ];

  posts: ForumPost[] = [
    {
      id: 1,
      title: 'How do you tell if an article is actually credible?',
      category: 'Fact Checking',
      description:
        'What are the first things you look for when checking whether an online article is trustworthy?',
      author: 'Alex',
      replies: 24,
      views: 318,
      time: '12 min ago',
      tag: 'Discussion',
      pinned: true,
    },
    {
      id: 2,
      title: 'Found an interesting article about AI misinformation',
      category: 'Media & News',
      description:
        'This article discusses how AI-generated content is changing the way misinformation spreads online.',
      author: 'Sarah',
      replies: 15,
      views: 241,
      time: '1 hr ago',
      tag: 'Article',
    },
    {
      id: 3,
      title: 'What sources do you trust the most?',
      category: 'General Discussion',
      description: 'Curious about which sources everyone uses when researching something online.',
      author: 'Daniel',
      replies: 31,
      views: 402,
      time: '2 hrs ago',
      tag: 'Discussion',
    },
    {
      id: 4,
      title: 'Suggestion: Add source comparison to reviews',
      category: 'Help & Feedback',
      description:
        'I think it would be useful if Dr.Kirk could compare multiple sources covering the same story.',
      author: 'Maya',
      replies: 9,
      views: 167,
      time: '4 hrs ago',
      tag: 'Suggestion',
    },
    {
      id: 5,
      title: 'Is a popular source automatically a reliable source?',
      category: 'Fact Checking',
      description:
        'A discussion about popularity, credibility, reputation, and how those things differ.',
      author: 'Ryan',
      replies: 18,
      views: 285,
      time: '6 hrs ago',
      tag: 'Discussion',
    },
    {
      id: 6,
      title: 'Share an article you think everyone should read',
      category: 'General Discussion',
      description:
        'Post something interesting and tell everyone why you think it is worth reading.',
      author: 'Emma',
      replies: 12,
      views: 194,
      time: 'Yesterday',
      tag: 'Community',
    },
  ];
}
