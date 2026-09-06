import { Component } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmTextareaImports } from '@spartan-ng/helm/textarea';
import { FormsModule } from '@angular/forms';

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

  imports: [RouterLink, HlmButtonImports, HlmTextareaImports , FormsModule,],

  templateUrl: './forum-post.html',
  styleUrl: './forum-post.css',
})
export class ForumPost {
  postId = 0;

  post: ForumPostData | undefined;

  posts: ForumPostData[] = [
    {
      id: 1,
      title: 'COVID-19 vaccines are causing cancer rates to skyrocket',
      category: 'General Discussion',
      description:
        'I recently read an article claiming that COVID-19 vaccines are linked to a significant increase in cancer rates. I am concerned about the validity of this claim and would like to discuss it with others.',
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
      author: 'Erika Kirk',
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
      author: 'Babario',
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
communityNote = '';

addCommunityNote(): void {
  const note = this.communityNote.trim();

  if (!note) {
    return;
  }

  console.log('Community note:', note);

  this.communityNote = '';
}
}
