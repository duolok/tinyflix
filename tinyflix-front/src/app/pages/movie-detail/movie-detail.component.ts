import { Component, ViewChild, ElementRef, OnInit } from "@angular/core";
import { CommonModule, DatePipe } from "@angular/common";
import { ActivatedRoute, Router } from "@angular/router";
import { ToastrService } from 'ngx-toastr';
import { MatDialog } from '@angular/material/dialog';
import { NavBarComponent } from "../../components/nav-bar/nav-bar.component";
import { MovieService } from "../../services/movie.service";
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { DeleteMovieDialogComponent } from '../../components/delete-movie-dialog/delete-movie-dialog.component';
import { DateFormatPipe } from '../../pipes/date-format.pipe';
import { RoundTwoDecimalsPipe } from '../../pipes/round-two-decimals.pipe';
import { PeopleFormatPipe } from '../../pipes/people-format.pipe';
import { RatingDialogComponent } from '../../components/rating-dialog/rating-dialog.component';
import { SubscriptionDialogComponent } from '../../components/subscription-dialog/subscription-dialog.component';
import { AuthService } from "../../services/auth.service";
import { RoleService } from "../../services/role.service";
import { FormsModule } from '@angular/forms'; 

@Component({
  selector: "app-movie-detail",
  standalone: true,
  imports: [CommonModule, FormsModule, NavBarComponent, MatDatepickerModule, MatNativeDateModule, MatInputModule, MatFormFieldModule, DateFormatPipe, RoundTwoDecimalsPipe, PeopleFormatPipe],
  providers: [DatePipe, RoundTwoDecimalsPipe],
  templateUrl: "./movie-detail.component.html",
  styleUrls: ["./movie-detail.component.scss"],
})
export class MovieDetailComponent implements OnInit {
  @ViewChild("videoPlayer") videoPlayer!: ElementRef<HTMLVideoElement>;
  movie: any;
  role: string = "user";
  isPlaying: boolean = false;
  showConfirmDialog = false;
  selectedResolution: string = "original";
  isAdmin: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private movieService: MovieService,
    private toastrService: ToastrService,
    private dialog: MatDialog,
    private authService: AuthService,
    private roleService: RoleService
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

    this.authService.getUserRole().then(() => {
      this.isAdmin = this.roleService.isAdmin();
    }).catch(error => {
        console.error('Error fetching user role:', error);
      });
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

  addSubscription(): void {
    this.showConfirmDialog = true;
    const dialogRef = this.dialog.open(SubscriptionDialogComponent, {
      width: '40%',
      backdropClass: 'backdropBackground',
      data: { movie: this.movie } 
    });

    dialogRef.afterClosed().subscribe(result => {
      this.showConfirmDialog = false;
      if (result) {
        this.toastrService.success('Subscribed successfully.');
      }
    });
  }


  rateMovie(): void {
    this.showConfirmDialog = true;
    const dialogRef = this.dialog.open(RatingDialogComponent, {
      width: '400px',
      data: { movieTitle: this.movie.name }
    });

    dialogRef.afterClosed().subscribe(result => {
      this.showConfirmDialog = false;
      if (result) {
        this.movieService.rateMovie(this.movie.name, result).subscribe(
          (response) => {
            this.toastrService.success('Rating added successfully.');
          },
          (error) => {
            console.error('Error adding rating', error);
            this.toastrService.error('Failed to add rating.');
          }
        );
      }
    });
  }

  updateMovie(): void {
    this.router.navigate(['/movie-update', this.movie.name]);
  }

  deleteMovie(): void {
    this.showConfirmDialog = true;
    const dialogRef = this.dialog.open(DeleteMovieDialogComponent, {
      width: "40%",
      backdropClass: "backdropBackground"
    });
    let movieName = this.movie.id;
    let folderId = this.movie.movieFilePath;

    dialogRef.afterClosed().subscribe(result => {
      this.showConfirmDialog = false;
      if (result) {
        this.movieService.deleteMovie(this.movie.name, this.movie.movieFilePath).subscribe(
          response => {
            this.toastrService.success('Movie deleted successfully.');
            this.router.navigateByUrl('/home');
          },
          error => {
            console.error('Error deleting movie', error);
            this.toastrService.error('Failed to delete movie.');
          }
        );
      }
    });
  }


  switchResolution(): void {
    const url = new URL(this.movie.movieFilePath);
    const baseFilePath = url.href.replace(/(_original|_360p|_480p|_720p)\.mp4$/, '');

    let newFilePath: string;
    switch (this.selectedResolution) {
      case '360p':
        newFilePath = `${baseFilePath}_360p.mp4`;
        break;
      case '480p':
        newFilePath = `${baseFilePath}_480p.mp4`;
        break;
      case '720p':
        newFilePath = `${baseFilePath}_720p.mp4`;
        break;
      default:
        newFilePath = `${baseFilePath}_original.mp4`;
        break;
    }

    this.movie.movieFilePath = newFilePath;
    console.log(`Updated movie file path: ${this.movie.movieFilePath}`);

    const video: HTMLVideoElement = this.videoPlayer.nativeElement;
    video.load(); 
  }
}

