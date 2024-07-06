import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { cognito } from '../../environments/environment'; 
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionService {
  private apiUrl = cognito.apiUrl;

  constructor(
    private httpClient: HttpClient,
    private authService: AuthService,
  ) { }

  subscribe(subscriptionCriteria: any): Observable<any> {
    return new Observable(observer => {
      this.authService.getUserId().then(email => {
        const headers = this.createAuthHeaders();
        const payload = {
          userId: email,
          subscriptionCriteria: subscriptionCriteria
        };
        console.log(payload);

        this.httpClient.put(`${this.apiUrl}/content-management`, payload, { headers }).pipe(
          catchError(error => {
            console.error('Error subscribing to content.', error);
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
      });
    });
  }

  getSubscriptions(): Observable<any> {
    return new Observable(observer => {
      this.authService.getUserId().then(email => {
        const headers = this.createAuthHeaders();
        console.log(email);
        this.httpClient.get(`${this.apiUrl}/content-management/get_subscriptions?email=${email}`, { headers }).pipe(
          catchError(error => {
            console.error('Error getting subscriptions.', error);
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
      });
    });
  }

  unsubscribe(subscriptionCriteria: any): Observable<any> {
    return new Observable(observer => {
      this.authService.getUserId().then(email => {
        const headers = this.createAuthHeaders();
        const payload = {
          userId: email,
          subscriptionCriteria: subscriptionCriteria
        };

        this.httpClient.post(`${this.apiUrl}/content-management/unsubscribe`, payload, { headers }).pipe(
          catchError(error => {
            console.error('Error cancelling subscription.', error);
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
      });
    });
  }

  private createAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (!token) {
      throw new Error('Authentication token is missing.');
    }
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }
}

