import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastrService } from 'ngx-toastr';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, FormControl, Validators } from '@angular/forms';
import { NavBarComponent } from '../../components/nav-bar/nav-bar.component';
import { UploadService } from '../../services/upload.service';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';

@Component({
  selector: 'app-movie-upload',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    NavBarComponent,
    MatDatepickerModule,
    MatNativeDateModule,
    MatInputModule,
    MatChipsModule,
    MatIconModule,
    MatFormFieldModule
  ],
  templateUrl: './movie-upload.component.html',
  styleUrls: ['./movie-upload.component.scss'],
})
export class MovieUploadComponent {
  uploadForm: FormGroup;
  fileMetadata: any = {};
  movieFile: File | null = null;
  imageFile: File | null = null;
  genresList: string[] = ['Romance', 'Action', 'Horror', 'Western', 'Sci-Fi', 'Comedy', 'Adventure', 'Crime', 'Biography', 'Drama'];
  actors: string[] = [];
  directors: string[] = [];

  actorCtrl = new FormControl('');
  directorCtrl = new FormControl('');

  readonly separatorKeysCodes: number[] = [ENTER, COMMA];
  selectable = true;
  removable = true;
  addOnBlur = true;

  constructor(
    private fb: FormBuilder,
    private movieUploadService: UploadService,
    private toastrService: ToastrService
  ) {
    this.uploadForm = this.fb.group({
      title: ['', Validators.required],
      duration: ['', Validators.required],
      releaseDate: ['', Validators.required],
      description: ['', Validators.required],
      genres: this.fb.array([], Validators.required),
    });
  }

  addActor(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    if (value) {
      this.actors.push(value);
    }
    event.chipInput!.clear();
    this.actorCtrl.setValue(null);
  }

  removeActor(actor: string): void {
    const index = this.actors.indexOf(actor);
    if (index >= 0) {
      this.actors.splice(index, 1);
    }
  }

  addDirector(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    if (value) {
      this.directors.push(value);
    }
    event.chipInput!.clear();
    this.directorCtrl.setValue(null);
  }

  removeDirector(director: string): void {
    const index = this.directors.indexOf(director);
    if (index >= 0) {
      this.directors.splice(index, 1);
    }
  }

  onFileChange(event: any, fileType: string) {
    const file = event.target.files[0];
    if (file) {
      this.fileMetadata[fileType] = {
        name: file.name,
        type: file.type,
        size: file.size,
        lastModified: new Date(file.lastModified),
        creationTime: new Date(file.lastModified),
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
        duration: this.uploadForm.get('duration')?.value,
        releaseDate: this.uploadForm.get('releaseDate')?.value,
        description: this.uploadForm.get('description')?.value,
        actors: this.actors,
        directors: this.directors,
        genres: this.uploadForm.get('genres')?.value,
        movieFilePath: `movies/${title}/${this.movieFile.name}`,
        imageFilePath: `movies/${title}/${this.imageFile.name}`,
        movieType: this.movieFile.type,
        movieSize: String(this.movieFile.size),
        movieLastModified: new Date(Date.now()),
        movieCreationTime: new Date(this.movieFile.lastModified),
        imageType: this.imageFile.type,
        imageSize: String(this.imageFile.size),
        imageLastModified: new Date(this.imageFile.lastModified),
        imageCreationTime: new Date(this.imageFile.lastModified),
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
        this.toastrService.error("An error has occurred. Try again later.");
      });
    }
  }
}

