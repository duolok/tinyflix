import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Inject } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { LoginService } from '../../services/login.service';
import { HeaderComponent } from '../../components/header/header.component';
import { MovieCategoryComponent } from '../../components/movie-category/movie-category.component';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [HeaderComponent, MovieCategoryComponent],
  templateUrl: './search.component.html',
  styleUrl: './search.component.scss'
})
export class SearchComponent {
  constructor(private loginService: LoginService, private router: Router, private toastrService: ToastrService) {}

  ngOnInit() {
    if(!this.loginService.isLoggedIn()) {
      this.router.navigateByUrl('/login');
    }
  }
}
