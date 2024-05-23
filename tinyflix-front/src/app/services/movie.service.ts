import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MovieService {
  constructor() {}

  getMovieDetailsByName(name: string): Observable<any> {
    const movies = [
      {
        name: 'sample-movie',
        title: 'Sample Movie',
        description: 'This is a sample movie description.',
        director: 'John Doe',
        cast: ['Actor 1', 'Actor 2'],
        releaseDate: '2021-01-01',
        duration: '120 mins',
        fileUrl: '../../assets/Vince Staples - Home (Spider-Man_ Into the Spider-Verse).mp4',
        bookmarks: []
      },
    ];

    const movie = movies.find(m => m.name === name);
    return of(movie); 
  }
}

