import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
@Component({
  selector: 'app-recommendation',
  templateUrl: './recommendation.component.html',
  styleUrls: ['./recommendation.component.css']
})
export class RecommendationComponent implements OnInit {
  recommendation: any;
  clientId: number = 1; // Valeur par défaut
  showRedirectMessage: boolean = true;

  constructor(
    private http: HttpClient,
      private router: Router
  ) {}

  ngOnInit(): void {
    const id = localStorage.getItem('client_id');
    this.clientId = id ? parseInt(id) : 1;

    this.http.get<any>(`http://127.0.0.1:8000/recommendation_multi/${this.clientId}`).subscribe({
      next: (res) => {
        this.recommendation = res;
      },
      error: (err) => {
        console.error('Erreur lors de la récupération de la recommandation:', err);
      }
    });
  }
  navigateToCreateProject() {
    this.router.navigate(['/creer']);
  }
  navigateToHome() {
    this.router.navigate(['/home']);
  }
}
