import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastrService } from 'ngx-toastr';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, FormControl, Validators } from '@angular/forms';
import { NavBarComponent } from '../../components/nav-bar/nav-bar.component';
import { UploadService } from '../../services/upload.service';

@Component({
  selector: 'app-movie-upload',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NavBarComponent],
  templateUrl: './movie-upload.component.html',
  styleUrls: ['./movie-upload.component.scss'],
})
export class MovieUploadComponent {

  uploadForm: FormGroup;
  fileMetadata: any = {};
  movieFile: File | null = null;
  imageFile: File | null = null;
  genresList: string[] = ['Romance', 'Action', 'Horror', 'Western', 'Sci-Fi', 'Comedy', 'Advneture', 'Crime'];
  constructor(
    private fb: FormBuilder,
    private movieUploadService: UploadService,
    private toastrService: ToastrService
  ) {
    this.uploadForm = this.fb.group({
      title: ['', Validators.required],
      description: ['', Validators.required],
      actors: ['', Validators.required],
      directors: ['', Validators.required],
      genres: this.fb.array([], Validators.required),
    });
  }

  onFileChange(event: any, fileType: string) {
    const file = event.target.files[0];
    if (file) {
      this.fileMetadata[fileType] = {
        name: file.name,
        type: file.type,
        size: file.size,
        creationTime: file.lastModifiedDate,
        lastModified: file.lastModifiedDate,
      };
      if (fileType === 'movie') {
        this.movieFile = file;
      } else if (fileType === 'image') {
        this.imageFile = file;
      }
    }
  }

  onCheckboxChange(event: any) {
    const genres: FormArray = this.uploadForm.get('genres') as FormArray;

    if (event.target.checked) {
      genres.push(new FormControl(event.target.value));
    } else {
      const index = genres.controls.findIndex(x => x.value === event.target.value);
      genres.removeAt(index);
    }
  }

  onSubmit() {
    if (this.uploadForm.valid && this.movieFile && this.imageFile) {
      const title = this.uploadForm.get('title')?.value;
      const metadata = {
        title: this.uploadForm.get('title')?.value,
        description: this.uploadForm.get('description')?.value,
        actors: this.uploadForm.get('actors')?.value,
        directors: this.uploadForm.get('directors')?.value,
        genres: this.uploadForm.get('genres')?.value,
        movieFilePath: `movies/${title}/${this.movieFile.name}`,
        imageFilePath: `movies/${title}/${this.imageFile.name}`
      };

      this.movieUploadService.getPresignedUrls([this.movieFile.name, this.imageFile.name], title).subscribe((response: any) => {
        const presignedUrls = response.upload_urls;
        this.toastrService.success("Uploading a movie... Please wait.");

        if (this.movieFile) {
          this.movieUploadService.uploadFile(presignedUrls[0], this.movieFile).subscribe(() => {
            if (this.imageFile) {
              this.movieUploadService.uploadFile(presignedUrls[1], this.imageFile).subscribe(() => {
                this.movieUploadService.saveMetadata(metadata).subscribe(metaResponse => {
                  console.log('Upload successful', metaResponse);
                  this.toastrService.success("Upload successful.");
                }, metaError => {
                  this.toastrService.error("Metadata save failed.");
                  });
              }, imageError => {
                  this.toastrService.error("Image upload failed.");
                });
            }
          }, movieError => {
              this.toastrService.error("Movie file upload failed.");
            });
        }
      }, urlError => {
          this.toastrService.error("An error has occured. Try again later.");
        });
    }
  }
}
