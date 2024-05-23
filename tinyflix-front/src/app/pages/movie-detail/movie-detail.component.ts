import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MovieService } from '../../services/movie.service';

@Component({
  selector: 'app-movie-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './movie-detail.component.html',
  styleUrls: ['./movie-detail.component.scss']
})
export class MovieDetailComponent implements OnInit {
  movie: any;
  role: string = 'user'; 

  constructor(
    private route: ActivatedRoute,
    private movieService: MovieService
  ) {}

  ngOnInit(): void {
    const movieName = this.route.snapshot.paramMap.get('name');
    if (movieName) {
      this.movieService.getMovieDetailsByName(movieName).subscribe((data) => {
        this.movie = data;
      });
    }
  }

  playMovie(): void {
  }

  downloadMovie(): void {
    const link = document.createElement('a');
    link.href = this.movie.fileUrl;
    link.download = this.movie.title;
    link.click();
  }

  addBookmark(): void {
    // Logic to add a bookmark
  }

  updateMovie(): void {
    // Logic to update the movie details (for admins)
  }
}
