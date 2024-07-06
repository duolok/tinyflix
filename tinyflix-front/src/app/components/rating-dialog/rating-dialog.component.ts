import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-rating-dialog',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './rating-dialog.component.html',
  styleUrl: './rating-dialog.component.scss'
})
export class RatingDialogComponent {
  movieTitle: string;
  rating: number = 0;

  constructor(
    public dialogRef: MatDialogRef<RatingDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.movieTitle = data.movieTitle;
  }

  close(): void {
    this.dialogRef.close();
  }

  onRateClick(): void {
    this.dialogRef.close(this.rating);
  }

  setRating(rating: number): void {
    this.rating = rating;
  }
}
