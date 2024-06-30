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

    // Clear the existing genres FormArray and repopulate it with the new genres
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
      const updatedMovie = {
        ...this.movie,
        title: this.updateForm.get('title')?.value,
        duration: this.updateForm.get('duration')?.value,
        releaseDate: this.updateForm.get('releaseDate')?.value,
        description: this.updateForm.get('description')?.value,
        actors: this.actors,
        directors: this.directors,
        genres: this.updateForm.get('genres')?.value,
        movieFilePath: this.movieFile ? `movies/${this.movie.name}/${this.movieFile.name}` : this.movie.movieFilePath,
        imageFilePath: this.imageFile ? `movies/${this.movie.name}/${this.imageFile.name}` : this.movie.imageFilePath,
        movieType: this.movieFile?.type,
        movieSize: this.movieFile?.size,
        movieLastModified: this.movieFile ? new Date(Date.now()) : this.movie.movieLastModified,
        movieCreationTime: this.movieFile ? new Date(this.movieFile.lastModified) : this.movie.movieCreationTime,
        imageType: this.imageFile?.type,
        imageSize: this.imageFile?.size,
        imageLastModified: this.imageFile ? new Date(this.imageFile.lastModified) : this.movie.imageLastModified,
        imageCreationTime: this.imageFile ? new Date(this.imageFile.lastModified) : this.movie.imageCreationTime,
      };

      this.movieService.updateMovie(updatedMovie).subscribe(
        (response) => {
          this.toastrService.success('Movie updated successfully.');
          this.router.navigate(['/movies', updatedMovie.name]);
        },
        (error) => {
          this.toastrService.error('Failed to update movie.');
          console.error('Error updating movie', error);
        }
      );
    }
  }
}

