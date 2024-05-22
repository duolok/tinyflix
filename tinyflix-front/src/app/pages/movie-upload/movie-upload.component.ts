import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NavBarComponent } from '../../components/nav-bar/nav-bar.component';

@Component({
  selector: 'app-movie-upload',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NavBarComponent],
  templateUrl: './movie-upload.component.html',
  styleUrls: ['./movie-upload.component.scss'],
})
export class MovieUploadComponent {
  uploadForm: FormGroup;
  fileMetadata: any;

  constructor(private fb: FormBuilder) {
    this.uploadForm = this.fb.group({
      title: ['', Validators.required],
      description: ['', Validators.required],
      actors: ['', Validators.required],
      directors: ['', Validators.required],
      genres: ['', Validators.required],
    });
  }

  onFileChange(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.fileMetadata = {
        name: file.name,
        type: file.type,
        size: file.size,
        creationTime: file.lastModifiedDate,
        lastModified: file.lastModifiedDate,
      };
    }
  }

  onSubmit() {
    if (this.uploadForm.valid) {
      const formData = new FormData();
      formData.append('file', this.fileMetadata);
      formData.append('title', this.uploadForm.get('title')?.value);
      formData.append('description', this.uploadForm.get('description')?.value);
      formData.append('actors', this.uploadForm.get('actors')?.value);
      formData.append('directors', this.uploadForm.get('directors')?.value);
      formData.append('genres', this.uploadForm.get('genres')?.value);

      // Call your upload service method here with formData
      // this.uploadService.uploadMovie(formData).subscribe(response => {
      //   console.log('Upload successful', response);
      // });
    }
  }
}

