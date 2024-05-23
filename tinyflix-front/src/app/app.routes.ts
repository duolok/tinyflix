import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { SignUpComponent } from './pages/sign-up/sign-up.component';
import { SearchComponent } from './pages/search/search.component';
import { MovieUploadComponent } from './pages/movie-upload/movie-upload.component';
import { MovieDetailComponent } from './pages/movie-detail/movie-detail.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: "login", component: LoginComponent },
  { path: "sign-up", component: SignUpComponent},
  { path: "movie/:name", component: MovieDetailComponent },
  { path: "movie-upload", component: MovieUploadComponent},
  { path: "search", component: SearchComponent, canActivate: [authGuard] },
  { path: "**", component: LoginComponent },
];
