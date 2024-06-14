import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Inject } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { LoginService } from '../../services/login.service';
import { HeaderComponent } from '../../components/header/header.component';
import { IUser, AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  email!: string;
  password!: string;
  loading: boolean;
  passwordVisible: boolean = false;
  user: IUser;

  constructor(
    private loginService: LoginService,
    private authService: AuthService,
    private router: Router,
    private toastrService: ToastrService) {
    this.loading = false;
    this.user = {} as IUser;
  }

  togglePasswordVisibility() {
    this.passwordVisible = !this.passwordVisible;
  }

  onSubmit() {
    console.log(this.user);
    this.loading = true;
    this.authService.signIn(this.user).then((res) => {
        this.router.navigateByUrl('/search');
        this.toastrService.success("Logged in successfully.");
        localStorage.setItem('token', res.signInUserSession.idToken.jwtToken)
      }).catch((err) => {
        this.loading = false;
        this.toastrService.error("Incorrect username or password.");
      })
  }

  openSignUp() {
    this.router.navigateByUrl('/sign-up');
  }
}
