import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = 'https://pk2brd8fo7.execute-api.eu-central-1.amazonaws.com/dev';

  constructor(private http: HttpClient) {}

  getPresignedUrls(files: string[], title: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/movies/upload-movie-file`, { files, title });
  }

  uploadFile(url: string, file: File): Observable<any> {
    return this.http.put(url, file, { responseType: 'text' });
  }

  saveMetadata(metadata: any): Observable<any> {
    console.log("METADATA ALO");
    console.log(metadata);
    return this.http.post(`${this.apiUrl}/movies/upload-movie-metadata`, metadata);
  }
}

