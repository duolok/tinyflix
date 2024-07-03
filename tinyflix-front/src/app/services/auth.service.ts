import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { Amplify, Auth } from 'aws-amplify';
import { cognito } from '../../environments/environment'; 

export interface IUser {
  email: string;
  username: string;
  password: string;
  firstName: string;
  lastName: string;
  birthdate: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private tokenSubject = new BehaviorSubject<string | null>(null);
  public token = this.tokenSubject.asObservable();

  constructor(private http: HttpClient) {
    Amplify.configure({
      Auth: cognito
    });

    this.loadToken();
  }

  private loadToken() {
    Auth.currentSession()
      .then(session => {
        const token = session.getIdToken().getJwtToken();
        this.tokenSubject.next(token);
        localStorage.setItem('token', token);
      })
      .catch(() => this.tokenSubject.next(null));
  }

  public signIn(user: IUser): Promise<any> {
    return Auth.signIn(user.email, user.password)
      .then(user => {
        this.loadToken();
        return user;
      });
  }

  public signOut(): Promise<any> {
    this.tokenSubject.next(null);
    localStorage.removeItem('token');
    return Auth.signOut();
  }

  public signUp(user: IUser): Promise<any> {
    return Auth.signUp({
      username: user.email,
      password: user.password,
      attributes: {
        birthdate: user.birthdate,
        name: user.firstName,
        family_name: user.lastName,
        nickname: user.username,
        'custom:role': user.role
      }
    }).then(result => {
      console.log("Sign Up Success: ", result);
      return result;
    }).catch(error => {
      console.error("Sign Up Error: ", error);
      throw error;
    });
  }

  public getCurrentUser(): Promise<any> {
    return Auth.currentUserInfo();
  }

  public updateUser(user: IUser): Promise<any> {
    return Auth.currentUserPoolUser()
      .then((cognitoUser: any) => {
        const attributes = {
          birthdate: user.birthdate,
          name: user.firstName,
          family_name: user.lastName,
          nickname: user.username,
          'custom:role': user.role
        };
        return Auth.updateUserAttributes(cognitoUser, attributes);
      });
  }

  public verifyUser(user: IUser, code: string): Promise<any> {
    return Auth.confirmSignUp(user.email, code);
  }

  public getToken(): string | null {
    return this.tokenSubject.value;
  }

  public getUserId(): Promise<string> {
    return this.getCurrentUser().then(user => user.attributes.email);
  }
}
