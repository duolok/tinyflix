import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Inject } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { LoginService } from '../../services/login.service';
import { HeaderComponent } from '../../components/header/header.component';
import { NavBarComponent } from '../../components/nav-bar/nav-bar.component';
import { MovieCategoryComponent } from '../../components/movie-category/movie-category.component';
import { FooterComponent } from '../../components/footer/footer.component';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [HeaderComponent, MovieCategoryComponent, NavBarComponent, FooterComponent],
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
