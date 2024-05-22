import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Inject } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { LoginService } from '../../services/login.service';
import { HeaderComponent } from '../../components/header/header.component';

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

  constructor(private loginService: LoginService, private router: Router, private toastrService: ToastrService) {}

  ngOnInit() {
    if(this.loginService.isLoggedIn()) {
      this.router.navigateByUrl('/search');
    }
  }

  onSubmit() {
    if(!this.email || !this.password) {
      this.toastrService.error("Provide email or password!");
      return;
    }
    this.toastrService.success("Logged in successfully.");
    this.loginService.login(this.email, this.password);
    this.router.navigateByUrl('/search');
  }

  openSignUp() {
    this.router.navigateByUrl('/sign-up');
  }
}
