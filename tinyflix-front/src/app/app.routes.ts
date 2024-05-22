import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { SignUpComponent } from './pages/sign-up/sign-up.component';
import { SearchComponent } from './pages/search/search.component';
import { NavBarComponent } from './components/nav-bar/nav-bar.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: "login", component: LoginComponent },
  { path: "sign-up", component: SignUpComponent},
  { path: "nav-bar", component: NavBarComponent },
  { path: "search", component: SearchComponent, canActivate: [authGuard] },
  { path: "**", component: LoginComponent },
];
