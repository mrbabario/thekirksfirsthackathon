import { Routes } from '@angular/router';

import { Homepage } from './pages/homepage/homepage';
import { SignIn } from './pages/sign-in/sign-in';

export const routes: Routes = [
  {
    path: '',
    component: Homepage
  },
  {
    path: 'sign-in',
    component: SignIn,
  },
];
