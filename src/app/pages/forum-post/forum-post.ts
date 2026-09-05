import { Component } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';

interface ForumPostData {
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
  selector: 'app-forum-post',
  standalone: true,

  imports: [RouterLink, HlmButtonImports, HlmTextareaImports],

  templateUrl: './forum-post.html',
  styleUrl: './forum-post.css',
})
export class ForumPost {
  postId = 0;

  post: ForumPostData | undefined;

  posts: ForumPostData[] = [
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
  ];

  constructor(private route: ActivatedRoute) {
    this.postId = Number(this.route.snapshot.paramMap.get('id'));

    this.post = this.posts.find((post) => post.id === this.postId);
  }
}
