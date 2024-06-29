import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-delete-movie-dialog',
  standalone: true,
  imports: [],
  templateUrl: './delete-movie-dialog.component.html',
  styleUrl: './delete-movie-dialog.component.scss'
})
export class DeleteMovieDialogComponent {
  constructor(public dialogRef: MatDialogRef<DeleteMovieDialogComponent>) {}

  confirmDelete(isConfirmed: boolean): void {
    this.dialogRef.close(isConfirmed);
  }}
