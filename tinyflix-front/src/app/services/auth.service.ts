import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
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

    constructor(private http: HttpClient) {
        Amplify.configure({
            Auth: cognito
        });
    }

    public signIn(user: IUser): Promise<any> {
        return Auth.signIn(user.email, user.password);
    }

    public signOut(): Promise<any> {
        localStorage.set('email', '');
        return Auth.signOut();
    }

    public signUp(user: IUser): Promise<any> {
        return Auth.signUp({
            username: user.email,
            password: user.password,
            attributes: {
                birthdate: user.birthdate, 
                name : user.firstName,
                family_name: user.lastName,
                nickname: user.username,
                'custom:role': 'User',
            }
        }).then(result => {
                console.log("Sign Up Success: ", result);
                return result;
            }).catch(error => {
                console.error("Sign Up Error: ", error);
                throw error;
            });
    }
    

    public getCurrentUser() : Promise<any> {
        return Auth.currentUserInfo();
    }

    public updateUser(user: IUser): Promise<any> {
        return Auth.currentUserPoolUser()
            .then((cognitoUser: any) => {
                return Auth.updateUserAttributes(cognitoUser, user);
            });
    }


    public verifyUser(user: IUser, code: string) : Promise<any> {
        return Auth.confirmSignUp(user.email, code);
    }
}
