import { Routes } from '@angular/router';

import { Homepage } from './pages/homepage/homepage';
import { SignIn } from './pages/sign-in/sign-in';
import { CreateAccount } from './pages/create-account/create-account';
import { Forum } from './pages/forum/forum';
import { ForumPost } from './pages/forum-post/forum-post';

export const routes: Routes = [
  {
    path: '',
    component: Homepage
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
    path: 'forum',
    component: Forum,
  },
  {
    path: 'forum/:id',
    component: ForumPost,
  },
];
