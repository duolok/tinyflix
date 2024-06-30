import { Component } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { NavBarComponent } from "../../components/nav-bar/nav-bar.component";
import { MovieCategoryComponent } from '../../components/movie-category/movie-category.component';
import { FooterComponent } from '../../components/footer/footer.component';
import { CommonModule, DatePipe } from "@angular/common";

@Component({
  selector: 'app-filter',
  standalone: true,
  imports: [CommonModule, NavBarComponent, MatIconModule, MovieCategoryComponent],
  templateUrl: './filter.component.html',
  styleUrl: './filter.component.scss'
})
export class FilterComponent {

}
