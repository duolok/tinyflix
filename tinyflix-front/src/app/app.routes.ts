import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { SignUpComponent } from './pages/sign-up/sign-up.component';
import { SearchComponent } from './pages/search/search.component';
import { FilterComponent } from './pages/filter/filter.component';
import { SubscriptionsComponent } from './pages/subscriptions/subscriptions.component';
import { MovieUploadComponent } from './pages/movie-upload/movie-upload.component';
import { MovieUpdateComponent } from './pages/movie-update/movie-update.component';
import { MovieDetailComponent } from './pages/movie-detail/movie-detail.component';
import { NotFoundComponent } from './pages/not-found/not-found.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: "login", component: LoginComponent },
  { path: "sign-up", component: SignUpComponent },
  { path: "movie/:name", component: MovieDetailComponent },
  { path: "movie-upload", component: MovieUploadComponent, canActivate: [authGuard], data: { roles: ['Admin'] } },
  { path: "movie-update/:name", component: MovieUpdateComponent, canActivate: [authGuard], data: { roles: ['Admin'] } },
  { path: "subscriptions", component: SubscriptionsComponent, canActivate: [authGuard], data: { roles: ['User', 'Admin'] } },
  { path: "search", component: FilterComponent, canActivate: [authGuard], data: { roles: ['User', 'Admin'] } },
  { path: "home", component: SearchComponent, canActivate: [authGuard], data: { roles: ['User', 'Admin'] } },
  { path: "not-found", component: NotFoundComponent },
  { path: "**", component: NotFoundComponent },
];
