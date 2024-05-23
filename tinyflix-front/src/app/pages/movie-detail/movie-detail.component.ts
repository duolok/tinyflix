import { Component, ViewChild, ElementRef, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ActivatedRoute } from "@angular/router";
import { NavBarComponent } from "../../components/nav-bar/nav-bar.component";
import { MovieService } from "../../services/movie.service";

@Component({
  selector: "app-movie-detail",
  standalone: true,
  imports: [CommonModule, NavBarComponent],
  templateUrl: "./movie-detail.component.html",
  styleUrls: ["./movie-detail.component.scss"],
})
export class MovieDetailComponent implements OnInit {
  @ViewChild("videoPlayer") videoPlayer!: ElementRef<HTMLVideoElement>;
  movie: any;
  role: string = "user";
  isPlaying: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private movieService: MovieService
  ) {}

  ngOnInit(): void {
    const movieName = this.route.snapshot.paramMap.get("name");
    if (movieName) {
      this.movieService.getMovieDetailsByName(movieName).subscribe((data) => {
        this.movie = data;
      });
    }
  }

  playMovie(): void {
    const video: HTMLVideoElement = this.videoPlayer.nativeElement;
    if (this.isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    this.isPlaying = !this.isPlaying;
  }

  downloadMovie(): void {
    const link = document.createElement("a");
    link.href = this.movie.fileUrl;
    link.download = this.movie.title;
    link.click();
  }

  addBookmark(): void { }
  updateMovie(): void { }
}

