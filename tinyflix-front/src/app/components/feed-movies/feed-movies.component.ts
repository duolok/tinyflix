import { Component, OnInit } from '@angular/core';
import { CommonModule } from "@angular/common";
import { MovieCardComponent } from '../movie-card/movie-card.component';
import { MovieService } from '../../services/movie.service'; 

@Component({
  selector: 'app-feed-movies',
  standalone: true,
  imports: [MovieCardComponent, CommonModule],
  templateUrl: './feed-movies.component.html',
  styleUrls: ['./feed-movies.component.scss']
})
export class FeedMoviesComponent implements OnInit {
  movies: any[] = []; 

  constructor(private movieService: MovieService) {}

  ngOnInit(): void {
    this.movieService.getFeedMovies().subscribe(movies => {
      this.movies = movies;
      console.log('Movies loaded:', this.movies);  
    }, error => {
      console.error('Error loading movies:', error);
    });
  }
}

