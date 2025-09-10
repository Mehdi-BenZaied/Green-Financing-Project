import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';  

export interface Answer {
  client_id: number;
  question_id: number;
  reponse_texte: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000';  
  private loggedIn = false; 
  constructor(private http: HttpClient) {}

  // ✅ Inscription
  signup(user: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register/`, user);
  }
  isAuthenticated(): boolean {
    const token = localStorage.getItem('auth_token');
    return this.loggedIn;  // Or you can check a token or session storage if needed
  }
  // ✅ Connexion
  login(credentials: { email: string; mot_de_passe: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/login/`, credentials).pipe(
      tap((response: any) => {
        if (response && response.user_id) {
          localStorage.setItem('client_id', response.user_id.toString());  
        }
      })
    );
  }
  checkIfAdmin(clientId: number): Observable<{ is_admin: boolean }> {
    return this.http.get<{ is_admin: boolean }>(`${this.apiUrl}/is-admin/${clientId}`);
  }
  
  canActivate(): boolean {
    const role = localStorage.getItem('role');
    if (role !== 'admin') {
      alert('⛔ Accès refusé');
      return false;
    }
    return true;
  }
  
  // ✅ Récupérer la liste des entreprises
  getEntreprises(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/entreprises/`);
  }

  // ✅ Récupérer la liste des questions
  getQuestions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/questions/`);
  }

  // ✅ Soumettre les réponses
  submitAnswers(answers: Answer[]): Observable<any> {
    console.log('Submitting answers:', answers);  
    return this.http.post<any>(`${this.apiUrl}/submit-answers/`, answers);
  }
}
