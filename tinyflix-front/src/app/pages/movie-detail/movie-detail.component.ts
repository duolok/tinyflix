import { Component, ViewChild, ElementRef, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ActivatedRoute } from "@angular/router";
import { ToastrService } from 'ngx-toastr';
import { MatDialog } from '@angular/material/dialog';
import { NavBarComponent } from "../../components/nav-bar/nav-bar.component";
import { MovieService } from "../../services/movie.service";
import { DeleteMovieDialogComponent } from '../../components/delete-movie-dialog/delete-movie-dialog.component';

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
  showConfirmDialog = false;

  constructor(
    private route: ActivatedRoute,
    private movieService: MovieService,
    private toastrService: ToastrService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    const movieName = this.route.snapshot.paramMap.get("name");
    if (movieName) {
      this.movieService.getMovieDetailsByName(movieName).subscribe(
        (data) => {
          this.movie = data;
        },
        (error) => {
          this.toastrService.error('Failed to load movie details.');
          console.error('Error loading movie details', error);
        }
      );
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
    if (this.movie && this.movie.movieFilePath) {
      this.toastrService.success("Downloading movie... Please wait.");
      this.movieService.downloadMovie(this.movie.movieFilePath).subscribe(
        async (presignedUrl) => {
          try {
            const response = await fetch(presignedUrl);
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.setAttribute('download', `${this.movie.name}.mp4`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href);
          } catch (error) {
            console.error('Error downloading the movie', error);
            this.toastrService.error('Failed to download the movie.');
          }
        },
        (error) => {
          console.error('Error getting presigned URL', error);
          this.toastrService.error('Failed to get download link.');
        }
      );
    }
  }

  addBookmark(): void {
    // Add bookmark implementation
  }

  updateMovie(): void {
    // Update movie implementation
  }

  deleteMovie(): void {
    this.showConfirmDialog = true;
    const dialogRef = this.dialog.open(DeleteMovieDialogComponent, {
      width: "40%",
      backdropClass: "backdropBackground"
    });

    dialogRef.afterClosed().subscribe(result => {
      this.showConfirmDialog = false;
      if (result) {
        this.movieService.deleteMovie(this.movie.id).subscribe(
          () => {
            this.toastrService.success('Movie deleted successfully.');
          },
          (error) => {
            console.error('Error deleting movie', error);
            this.toastrService.error('Failed to delete movie.');
          }
        );
      }
    });
  }
}
