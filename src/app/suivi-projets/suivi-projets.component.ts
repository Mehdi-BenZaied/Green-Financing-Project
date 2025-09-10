import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-suivi-projets',
  templateUrl: './suivi-projets.component.html',
  styleUrls: ['./suivi-projets.component.css']
})
export class SuiviProjetsComponent implements OnInit {
  projets: any[] = [];
  errorMessage: string = '';
  clientId: string | null = localStorage.getItem('user_id');

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    if (this.clientId) {
      this.http.get(`http://127.0.0.1:8000/projets/by-client/${this.clientId}`).subscribe({
        next: (data: any) => {
          this.projets = data;
        },
        error: (error) => {
          console.error('Erreur de récupération des projets :', error);
          this.errorMessage = "Impossible de charger les projets.";
        }
      });
    } else {
      this.errorMessage = "Aucun identifiant client trouvé.";
    }
  }
}
