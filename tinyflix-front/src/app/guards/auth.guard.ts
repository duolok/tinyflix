import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { LoginService } from '../services/login.service';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const loginService = inject(LoginService);
  /*
    if (userRole == null || !route.data['role'].includes(userRole)) {
      router.navigate(['home']);
      return false;
    }
*/

  if (!loginService.isLoggedIn) {
    return router.createUrlTree(["/login"]);
  } else {
    return true;
  }
};
