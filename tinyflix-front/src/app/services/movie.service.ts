import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, forkJoin } from 'rxjs';
import { cognito } from '../../environments/environment'; 
import { AuthService } from './auth.service';
import { catchError, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class MovieService {
  private apiUrl = cognito.apiUrl;
  private s3BucketUrl = cognito.s3BucketUrl;

  constructor(
    private httpClient: HttpClient,
    private authService: AuthService,
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
      }),
      catchError(error => {
        console.error('Error fetching movies.', error);
        return throwError(error);
      })
    );
  }

  downloadMovie(filePath: string): Observable<string> {
    const fileKey = filePath.substring(filePath.indexOf('movies/'));
    const params = new HttpParams().set('file_key', fileKey);
    const headers = this.createAuthHeaders();
    return this.httpClient.get<{ presigned_url: string }>(`${this.apiUrl}/movies/download-movie-file`, { params, headers }).pipe(
      map(response => response.presigned_url),
      catchError(error => {
        console.error('Error downloading movie.', error);
        return throwError(error);
      })
    );
  }

  updateMovie(movie: any): Observable<any> {
    return this.httpClient.patch(`${this.apiUrl}/update-movie/${movie.name}`, movie);
  }


  searchMovies(searchQuery: string): Observable<any[]> {
    const headers = this.createAuthHeaders();
    const params = new HttpParams().set('searchQuery', searchQuery);

    return this.httpClient.get<any[]>(`${this.apiUrl}/movies/search`, { headers, params }).pipe(
      map(response => {
        const movies = response; 
        return movies.map((movie: any) => ({
          ...movie,
          actors: movie.actors.split('|'),  
          directors: movie.directors.split('|'),  
          genres: movie.genres.split('|'),  
          movieFilePath: `${this.s3BucketUrl}/${movie.movieFilePath}`,
          imageFilePath: `${this.s3BucketUrl}/${movie.imageFilePath}`
        }));
      }),
      catchError(error => {
        console.error('Error searching movies.', error);
        return throwError(error);
      })
    );
  }


  deleteMovie(movieName: string, movieFilePath: string): Observable<any> {
    const headers = this.createAuthHeaders();
    const fileDeleteUrl = `${this.apiUrl}/movies/delete-movie-file`;
    const metadataDeleteUrl = `${this.apiUrl}/movies/delete-movie-metadata`;

    const fileDeletePayload = {
      body: { movieFilePath } 
    };
    const metadataDeletePayload = {
      'body': JSON.stringify({ movie_name: movieName })
    };
    console.log(metadataDeletePayload);

    return forkJoin([
      this.httpClient.request('DELETE', fileDeleteUrl, { headers, body: fileDeletePayload.body }),
      this.httpClient.request('DELETE', metadataDeleteUrl, { headers, body: metadataDeletePayload.body })
    ]).pipe(
        map(responses => ({ 
          fileDeletionResponse: responses[0], 
          metadataDeletionResponse: responses[1] 
        })),
        catchError(error => {
          console.error('Error deleting movie.', error);
          return throwError(error);
        })
      );
  }

  private createAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (!token) {
      throw new Error('Authentication token is missing.');
    }
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }
}
