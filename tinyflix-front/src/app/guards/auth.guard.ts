import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { inject } from '@angular/core';
import { LoginService } from '../services/login.service';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const loginService = inject(LoginService);

  if (!loginService.isLoggedIn) {
    return router.createUrlTree(["/login"]);
  }

  const userRole = localStorage.getItem('userRole'); 

  if (!userRole || !route.data['roles'].includes(userRole)) {
    return router.createUrlTree(["/not-found"]); 
  }

  return true;
};

