import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-unsubscribe-dialog',
  standalone: true,
  imports: [],
  templateUrl: './unsubscribe-dialog.component.html',
  styleUrl: './unsubscribe-dialog.component.scss'
})
export class UnsubscribeDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<UnsubscribeDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  confirmDelete(isConfirmed: boolean): void {
    this.dialogRef.close(isConfirmed);
  }
}
