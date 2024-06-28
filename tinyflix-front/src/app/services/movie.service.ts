import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { cognito } from '../../environments/environment'; 

@Injectable({
  providedIn: 'root'
})
export class MovieService {
  private apiUrl = cognito.apiUrl;
  private s3BucketUrl = cognito.s3BucketUrl;

  constructor(
    private httpClient: HttpClient,
  ) {}

  getMovieDetailsByName(name: string): Observable<any> {
    return this.getMovies().pipe(
      map(movies => movies.find(movie => movie.name === name))
    );
  }

  getMovies(): Observable<any[]> {
    return this.httpClient.get<{ body: string }>(`${this.apiUrl}/movies/get-all-movies`).pipe(
      map(response => {
        const parsedBody = JSON.parse(response.body);
        const movies = parsedBody.data;
        return movies.map((movie: any) => ({
          ...movie,
          imageFilePath: `${this.s3BucketUrl}/${movie.imageFilePath}`,
          movieFilePath: `${this.s3BucketUrl}/${movie.movieFilePath}`
        }));
      })
    );
  }

  private getMoviesList(): any[] {
    return [];
  }
}

