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

  constructor(private movieService: MovieService) {}

  ngOnInit(): void {
    this.movieService.getMovies().subscribe(movies => {
      this.movies = movies;
      console.log(this.movies)
    });
  }

}

