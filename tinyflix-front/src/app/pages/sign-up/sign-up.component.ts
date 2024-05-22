import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Inject } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { LoginService } from '../../services/login.service';
import { HeaderComponent } from '../../components/header/header.component';

@Component({
  selector: 'app-sign-up',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.scss',
})
export class SignUpComponent {
  firstName!: string;
  lastName!: string;
  birthday!: Date;
  email!: string;
  username!: string;
  password!: string;

  constructor(
    private loginService: LoginService,
    private router: Router,
    private toastrService: ToastrService,
  ) {}

  ngOnInit() {
    if (this.loginService.isLoggedIn()) {
      this.router.navigateByUrl('/search');
    }
  }

  onSubmit() {
    if (!this.firstName || !this.lastName || !this.birthday || !this.email || !this.username || !this.password) {
      this.toastrService.error('All fields are required!');
      return;
    }
    // You may want to replace this with actual sign-up logic
    this.toastrService.success('Signed up successfully.');
    this.loginService.login(this.email, this.password);
    this.router.navigateByUrl('/search');
  }

  openLogin() {
    this.router.navigateByUrl('/');
  }
}

