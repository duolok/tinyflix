import { Component, OnInit } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { NavBarComponent } from "../../components/nav-bar/nav-bar.component";
import { MovieCardComponent } from '../../components/movie-card/movie-card.component';
import { CommonModule } from "@angular/common";
import { Router } from '@angular/router';
import { MovieService } from '../../services/movie.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-filter',
  standalone: true,
  imports: [CommonModule, NavBarComponent, MatIconModule, MovieCardComponent, FormsModule],
  templateUrl: './filter.component.html',
  styleUrls: ['./filter.component.scss']
})
export class FilterComponent implements OnInit {
  movies: any = [];
  searchQuery: string = '';

  constructor(private router: Router, private movieService: MovieService) {}

  ngOnInit() {}

  searchMovies() {
    this.movieService.searchMovies(this.searchQuery).subscribe(
      response => {
        console.log('Search response:', response);
        this.movies = response;
      },
      error => {
        console.error('Error searching movies.', error);
      }
    );
  }
}

