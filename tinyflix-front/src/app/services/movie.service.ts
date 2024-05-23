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
        title: 'Spider-Man: Into the Spider-Verse',
        description: 'Teen Miles Morales becomes the Spider-Man of his universe and must join with five spider-powered individuals from other dimensions to stop a threat for all realities.',
        director: ['Bob Persichetti', 'Peter Ramsey', 'Rodney Rothman'],
        cast: ['Shameik Moore', 'Jake Johnson', 'Hailee Steinfeld'],
        releaseDate: '2018-12-14',
        duration: '120 mins',
        fileUrl: '../../assets/Vince Staples - Home (Spider-Man_ Into the Spider-Verse).mp4',
        bookmarks: []
      },
    ];

    const movie = movies.find(m => m.name === name);
    return of(movie); 
  }
}

