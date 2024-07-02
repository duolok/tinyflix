import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastrService } from 'ngx-toastr';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, FormControl, Validators } from '@angular/forms';
import { NavBarComponent } from '../../components/nav-bar/nav-bar.component';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';
import { ActivatedRoute, Router } from '@angular/router';
import { MovieService } from '../../services/movie.service';
import { forkJoin, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

interface FileToUpload {
  file: File;
  key: string;
}

@Component({
  selector: 'app-movie-update',
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
  templateUrl: './movie-update.component.html',
  styleUrls: ['./movie-update.component.scss']
})
export class MovieUpdateComponent implements OnInit {
  updateForm: FormGroup;
  movie: any;
  fileMetadata: { [key: string]: any } = {};
  movieFile: File | null = null;
  imageFile: File | null = null;
  genresList: string[] = ['Romance', 'Action', 'Horror', 'Western', 'Sci-Fi', 'Comedy', 'Adventure', 'Crime'];
  actors: string[] = [];
  directors: string[] = [];

  actorCtrl = new FormControl('');
  directorCtrl = new FormControl('');

  readonly separatorKeysCodes: number[] = [ENTER, COMMA];
  selectable = true;
  removable = true;
  addOnBlur = true;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private movieService: MovieService,
    private toastrService: ToastrService
  ) {
    this.updateForm = this.fb.group({
      title: ['', Validators.required],
      duration: ['', Validators.required],
      releaseDate: ['', Validators.required],
      description: ['', Validators.required],
      genres: this.fb.array([], Validators.required),
    });
  }

  ngOnInit(): void {
    const movieName = this.route.snapshot.paramMap.get("name");
    if (movieName) {
      this.movieService.getMovieDetailsByName(movieName).subscribe(
        (data) => {
          this.movie = data;
          this.movie.actors = this.movie.actors ? this.movie.actors.split('|').map((actor: string) => actor.trim()) : [];
          this.movie.directors = this.movie.directors ? this.movie.directors.split('|').map((director: string) => director.trim()) : [];
          this.movie.genres = this.movie.genres ? this.movie.genres.split('|').map((genre: string) => genre.trim()) : [];
          this.populateForm();
        },
        (error) => {
          this.toastrService.error('Failed to load movie details.');
          console.error('Error loading movie details', error);
        }
      );
    }
  }

  populateForm(): void {
    this.updateForm.patchValue({
      title: this.movie.title,
      duration: this.movie.duration,
      releaseDate: this.movie.releaseDate,
      description: this.movie.description,
    });
    this.actors = this.movie.actors;
    this.directors = this.movie.directors;

    const genresArray = this.updateForm.get('genres') as FormArray;
    genresArray.clear();
    this.movie.genres.forEach((genre: string) => {
      genresArray.push(new FormControl(genre));
    });
  }

  isGenreChecked(genre: string): boolean {
    const genresArray = this.updateForm.get('genres') as FormArray;
    return genresArray.controls.some(control => control.value === genre);
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

  onCheckboxChange(event: any) {
    const genres: FormArray = this.updateForm.get('genres') as FormArray;
    if (event.target.checked) {
      genres.push(new FormControl(event.target.value));
    } else {
      const index = genres.controls.findIndex(x => x.value === event.target.value);
      genres.removeAt(index);
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

  onSubmit() {
    if (this.updateForm.valid) {
      const updatedMovie: any = {
        ...this.movie,
        title: this.updateForm.get('title')?.value,
        duration: this.updateForm.get('duration')?.value,
        releaseDate: this.updateForm.get('releaseDate')?.value,
        description: this.updateForm.get('description')?.value,
        actors: this.actors.join('|'),
        directors: this.directors.join('|'),
        genres: (this.updateForm.get('genres')?.value || []).join('|'),
      };

      if (this.movieFile) {
        updatedMovie.movieFilePath = `movies/${this.movie.name}/${this.movieFile.name}`;
        updatedMovie.movieFileType = this.movieFile.type;
        updatedMovie.movieFileSize = this.movieFile.size;
        updatedMovie.movieFileCreationTime = new Date(this.movieFile.lastModified);
        updatedMovie.movieFileLastModified = new Date(this.movieFile.lastModified);
      }

      if (this.imageFile) {
        updatedMovie.imageFilePath = `movies/${this.movie.name}/${this.imageFile.name}`;
        updatedMovie.imageFileType = this.imageFile.type;
        updatedMovie.imageFileSize = this.imageFile.size;
        updatedMovie.imageFileCreationTime = new Date(this.imageFile.lastModified);
        updatedMovie.imageFileLastModified = new Date(this.imageFile.lastModified);
      }

      const payload = {
        object: updatedMovie,
      };

      const filesToUpload: FileToUpload[] = [];
      if (this.movieFile) {
        filesToUpload.push({ file: this.movieFile, key: updatedMovie.movieFilePath });
      }
      if (this.imageFile) {
        filesToUpload.push({ file: this.imageFile, key: updatedMovie.imageFilePath });
      }

      if (filesToUpload.length > 0) {
        const fileNames = filesToUpload.map(file => file.key);
        this.movieService.getPresignedUrls(fileNames, this.movie.name).subscribe(
          (presignedUrls) => {
            const uploadObservables: Observable<any>[] = filesToUpload.map((fileToUpload, index) => 
              this.movieService.uploadFile(presignedUrls.upload_urls[index], fileToUpload.file).pipe(
                map(() => {
                  if (fileToUpload.file === this.movieFile) {
                    updatedMovie.movieFilePath = fileToUpload.key;
                  } else if (fileToUpload.file === this.imageFile) {
                    updatedMovie.imageFilePath = fileToUpload.key;
                  }
                })
              )
            );

            forkJoin(uploadObservables).subscribe(() => {
              this.updateMovie(payload);
            });
          },
          (error) => {
            this.toastrService.error('Failed to get presigned URLs.');
            console.error('Error getting presigned URLs', error);
          }
        );
      } else {
        this.updateMovie(payload);
      }
    }
  }

  private updateMovie(payload: any) {
    this.movieService.updateMovie(payload).subscribe(
      (response) => {
        this.toastrService.success('Movie updated successfully.');
        this.router.navigate(['/movie', payload.object.name]);
      },
      (error) => {
        this.toastrService.error('Failed to update movie.');
        console.error('Error updating movie', error);
      }
    );
  }
}

