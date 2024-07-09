import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from "@angular/common";
import { MovieCardComponent } from '../movie-card/movie-card.component';
import { MovieService } from '../../services/movie.service'; 

@Component({
  selector: 'app-movie-category',
  standalone: true,
  imports: [MovieCardComponent, CommonModule],
  templateUrl: './movie-category.component.html',
  styleUrls: ['./movie-category.component.scss']
})
export class MovieCategoryComponent implements OnInit {
  @Input() title: string = "";
  movies: any[] = []; 
  recentMovies: any[] = []; 

  constructor(private movieService: MovieService) {}

  ngOnInit(): void {
    this.movieService.getMovies().subscribe(movies => {
      this.movies = movies;
      this.recentMovies = this.getRecentMovies();
    });
  }

  getRecentMovies(): any[] {
    return this.movies
      .sort((a, b) => new Date(b.releaseDate).getTime() - new Date(a.releaseDate).getTime())
      .slice(0, 5);
  }
}
