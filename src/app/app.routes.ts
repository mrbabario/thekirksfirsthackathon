import { Routes } from '@angular/router';

import { Homepage } from './pages/homepage/homepage';
import { SignIn } from './pages/sign-in/sign-in';
import { CreateAccount } from './pages/create-account/create-account';
import { Forum } from './pages/forum/forum';
import { ForumPost } from './pages/forum-post/forum-post';
import { CreatePost } from './pages/create-post/create-post';
import { ReviewPage } from './pages/review/review';
import { AsdfPost } from './pages/asdf-post/asdf-post';

export const routes: Routes = [
  {
    path: '',
    component: Homepage,
  },
  {
    path: 'sign-in',
    component: SignIn,
  },
  {
    path: 'create-account',
    component: CreateAccount,
  },
  {
    path: 'review',
    component: ReviewPage ,
  },
  {
    path: 'forum',
    component: Forum,
  },
  {
    path: 'forum/create',
    component: CreatePost,
  },
  {
    path: 'forum/:id',
    component: ForumPost,
  },
  {
    path: 'asdf-post',
    component: AsdfPost,
  },
];
