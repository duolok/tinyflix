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
  selector: 'app-sign-up',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.scss',
})
export class SignUpComponent {
  loading: boolean;
  isSignIn: boolean = true;
  isVerification: boolean = false;

  isConfirmed: boolean;
  verificationEmail: string = '';
  verificationCode: string = '';
  user: IUser;


  constructor(
    private loginService: LoginService,
    private authService: AuthService,
    private router: Router,
    private toastrService: ToastrService,
  ) {
    this.loading = false;
    this.isConfirmed = false;
    this.user = {} as IUser;
  }

  toggleVerification() {
    if (!this.isSignIn) this.toggleSignUp()
    this.isVerification = !this.isVerification
  }

  toggleSignUp() {
    this.isSignIn = !this.isSignIn
  }

  ngOnInit() {
    if (this.loginService.isLoggedIn()) {
      this.router.navigateByUrl('/home');
    }
  }

  public signUp(): void {
    this.loading = true;
    this.authService.signUp(this.user)
      .then(() => {
        this.loading = false;
        this.isConfirmed = true;
        this.toastrService.success("Verification link has been sent.");
        this.toggleVerification();
      }).catch(() => {
        this.loading = false;
      });
  }

  public confirmSignUp(): void {
    this.loading = true;
    this.authService.verifyUser(this.user, this.verificationCode)
      .then(() => {
        this.toastrService.success("Verification successful.");
        this.router.navigate(['/']);
      }).catch(() => {
        this.loading = false;
        this.toggleVerification();
      });
  }

  openLogin() {
    this.router.navigateByUrl('/');
  }
}

