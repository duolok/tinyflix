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
        console.log(movies);
        return movies.map((movie: any) => ({
          ...movie,
          movieFilePath: `${this.s3BucketUrl}/${movie.movieFilePath}`,
          imageFilePath: `${this.s3BucketUrl}/${this.addOriginalSuffix(movie.imageFilePath)}`,
        }));
      }),
      catchError(error => {
        console.error('Error fetching movies.', error);
        return throwError(error);
      })
    );
  }

  addOriginalSuffix(filePath: string): string {
    const parts = filePath.split('.');
    if (parts.length > 1) {
      parts[parts.length - 2] += '_original';
    }
    return parts.join('.');
  }


  downloadMovie(filePath: string): Observable<string> {
    const fileKey = filePath.substring(filePath.indexOf('movies/'));

    return new Observable(observer => {
      this.authService.getUserId().then(email => {
        const params = new HttpParams()
        .set('file_key', fileKey)
        .set('email', email); 
        const headers = this.createAuthHeaders();

        this.httpClient.get<{ presigned_url: string }>(`${this.apiUrl}/movies/download-movie-file`, { params, headers }).pipe(
          map(response => response.presigned_url),
          catchError(error => {
            console.error('Error downloading movie.', error);
            return throwError(error);
          })
        ).subscribe(
            presignedUrl => {
              observer.next(presignedUrl);
              observer.complete();
            },
            error => {
              observer.error(error);
            }
          );
      }).catch(error => {
          console.error('Error getting user email.', error);
          observer.error(error);
        });
    });
  }

  rateMovie(movieId: string, rating: number): Observable<any> {
    return new Observable(observer => {
      this.authService.getUserId().then(email => {
        const headers = this.createAuthHeaders();
        const body = {
          movie_id: movieId,
          email: email, 
          rating: rating
        };
        this.httpClient.patch(`${this.apiUrl}/movies/rate-movie`, body, { headers }).pipe(
          catchError(error => {
            console.error('Error rating movie.', error);
            return throwError(error);
          })
        ).subscribe(
            response => {
              observer.next(response);
              observer.complete();
            },
            error => {
              observer.error(error);
            }
          );

      }).catch(error => {
          observer.error(error);
        })
    })

  }

  updateMovie(movie: any): Observable<any> {
    const headers = this.createAuthHeaders();
    return this.httpClient.patch(`${this.apiUrl}/movies/update-movie`, movie, { headers });
  }


  getPresignedUrls(files: string[], title: string): Observable<any> {
    return this.httpClient.put(`${this.apiUrl}/movies/upload-movie-file`, { files, title });
  }

  uploadFile(url: string, file: File): Observable<any> {
    return this.httpClient.put(url, file, { responseType: 'text' });
  }

  saveMetadata(metadata: any): Observable<any> {
    return this.httpClient.post(`${this.apiUrl}/movies/upload-movie-metadata`, metadata);
  }


  searchMovies(searchQuery: string): Observable<any[]> {
    const headers = this.createAuthHeaders();
    const params = new HttpParams().set('searchQuery', searchQuery);

    return this.httpClient.get<any>(`${this.apiUrl}/movies/search`, { headers, params }).pipe(
      map(response => {
        const movies = Array.isArray(response) ? response : response.data; 
        return movies.map((movie: any) => ({
          ...movie,
          actors: movie.actors.split('|'),  
          directors: movie.directors.split('|'),  
          genres: movie.genres.split('|'),  
          movieFilePath: `${this.s3BucketUrl}/${movie.movieFilePath}`,
          imageFilePath: `${this.s3BucketUrl}/${this.addOriginalSuffix(movie.imageFilePath)}`
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

    const url = new URL(movieFilePath);
    const fullPath = url.pathname;
    const directoryPath = fullPath.substring(1, fullPath.lastIndexOf('/'));
    console.log(directoryPath);

    const fileDeletePayload = {
      body: { movieFilePath: directoryPath }
    };
    const metadataDeletePayload = {
      'body': JSON.stringify({ movie_name: movieName })
    };

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

  getFeedMovies(): Observable<any[]> {
    return new Observable(observer => {
      this.authService.getUserId().then(userId => {
        const params = new HttpParams().set('userId', userId);
        const headers = this.createAuthHeaders();

        this.httpClient.get<any>(`${this.apiUrl}/content-management/get-feed`, { params, headers }).pipe(
          map(response => {
            console.log('API Response:', response);  

            if (!response || !Array.isArray(response.data)) {
              console.error('Invalid response format:', response);
              return [];
            }

            const movies = response.data.reduce((acc: any[], item: any) => {
              if (!item.movies || !Array.isArray(item.movies)) {
                console.error('Invalid movies format in item:', item);
                return acc;
              }

              const processedMovies = item.movies.map((movieItem: any) => {
                const movie = movieItem.movie || {};
                console.log('Processing movie item:', movieItem);
                return {
                  ...movie,
                  actors: movie.actors ? movie.actors.split('|') : [],
                  directors: movie.directors ? movie.directors.split('|') : [],
                  genres: movie.genres ? movie.genres.split('|') : [],
                  movieFilePath: movie.movieFilePath ? `${this.s3BucketUrl}/${movie.movieFilePath}` : '',
                  imageFilePath: movie.imageFilePath ? `${this.s3BucketUrl}/${this.addOriginalSuffix(movie.imageFilePath)}` : '',
                  score: movieItem.score || 0
                };
              });

              return acc.concat(processedMovies);
            }, []);

            console.log('Processed movies:', movies);
            return movies;
          }),
          catchError(error => {
            console.error('Error fetching feed movies:', error);
            return throwError(error);
          })
        ).subscribe(
            movies => {
              observer.next(movies);
              observer.complete();
            },
            error => {
              observer.error(error);
            }
          );
      }).catch(error => {
          console.error('Error getting user ID:', error);
          observer.error(error);
        });
    });
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

