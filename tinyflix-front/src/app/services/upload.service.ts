import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { cognito } from '../../environments/environment'; 

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private apiUrl = cognito.apiUrl;

  constructor(private http: HttpClient) {}

  getPresignedUrls(files: string[], title: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/movies/upload-movie-file`, { files, title });
  }

  uploadFile(url: string, file: File): Observable<any> {
    return this.http.put(url, file, { responseType: 'text' });
  }

  saveMetadata(metadata: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/movies/upload-movie-metadata`, metadata);
  }
}

