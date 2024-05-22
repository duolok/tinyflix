import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LoginService {

  constructor() { }

  login(email: string, password: string) {
    // call api here
    // set token
    localStorage.setItem("token", Math.random() + "")
  }

  isLoggedIn() {
    if(localStorage.getItem('token')) {
      return true;
    }
    return false;
  }
}
