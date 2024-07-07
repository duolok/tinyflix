import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { SubscriptionService } from '../../services/subscription.service';
import { ToastrService } from 'ngx-toastr';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-subscription-dialog',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './subscription-dialog.component.html',
  styleUrls: ['./subscription-dialog.component.scss']
})
export class SubscriptionDialogComponent {
  movie: any;
  criteriaOptions: string[] = ['Actors', 'Directors', 'Genres'];
  selectedCriteria: string = '';
  selectedActors: string[] = [];
  selectedDirectors: string[] = [];
  selectedGenres: string[] = [];

  actors: string[] = [];
  directors: string[] = [];
  genres: string[] = [];

  constructor(
    public dialogRef: MatDialogRef<SubscriptionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private subscriptionService: SubscriptionService,
    private toastrService: ToastrService
  ) {
    this.movie = data.movie;
    this.actors = this.movie.actors.split('|').map((actor: string) => actor.trim());
    this.directors = this.movie.directors.split('|').map((director: string) => director.trim());
    this.genres = this.movie.genres.split('|').map((genre: string) => genre.trim());
  }

  close(): void {
    this.dialogRef.close();
  }

  subscribe(): void {
    const subscriptionCriteria = {
      actors: this.selectedActors,
      directors: this.selectedDirectors,
      genres: this.selectedGenres
    };

    this.subscriptionService.subscribe(subscriptionCriteria, this.movie.name).subscribe(
      () => {
        this.toastrService.success('Subscribed successfully!');
        this.dialogRef.close();
      },
      error => {
        console.error('Error subscribing:', error);
        this.toastrService.error('Failed to subscribe.');
      }
    );
  }
}

