import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { cognito } from '../../environments/environment'; 
import { AuthService } from './auth.service';

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
        console.error('Error downloading movie', error);
        return throwError(error);
      })
    );
  }

  private createAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (!token) {
      throw new Error('Authentication token is missing');
    }
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  private getMoviesList(): any[] {
    return [];
  }
}

