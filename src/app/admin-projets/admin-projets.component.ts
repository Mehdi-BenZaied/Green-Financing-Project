import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-admin-projets',
  templateUrl: './admin-projets.component.html',
  styleUrls: ['./admin-projets.component.css']
})
export class AdminProjetsComponent implements OnInit {
  projets: any[] = [];
  errorMessage = '';
  successMessage = '';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchProjets();
  }

  fetchProjets(): void {
    this.http.get<any[]>('http://127.0.0.1:8000/projets/all').subscribe({
      next: (res) => {
        this.projets = res;
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = '❌ Impossible de charger les projets.';
      }
    });
  }

  updateStatut(projetId: number, statut: string): void {
    this.http.put(`http://127.0.0.1:8000/projets/${projetId}/statut`, { statut }).subscribe({
      next: () => {
        this.successMessage = '✅ Statut mis à jour avec succès.';
        this.fetchProjets();
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = "❌ Impossible de mettre à jour le statut.";
      }
    });
  }
}
