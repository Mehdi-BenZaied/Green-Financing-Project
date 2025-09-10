import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-admin-reponses',
  templateUrl: './admin-reponses.component.html',
  styleUrls: ['./admin-reponses.component.css']
})
export class AdminReponsesComponent implements OnInit {
  reponses: any[] = [];
  entreprises: any[] = []; // Liste des entreprises pour filtrer
  filtreEntreprise: string = ''; // Filtre par entreprise
  filtreDate: string = ''; // Filtre par date
  editingReponse: boolean = false; // Pour savoir si on est en mode édition
  reponseModifiee: any = {}; // Réponse en cours de modification

  constructor(private http: HttpClient, private authService: AuthService) {}

  ngOnInit(): void {
    // Récupérer les réponses et les entreprises au démarrage
    this.getReponses();
    this.getEntreprises();
  }

  // Récupérer les réponses depuis l'API avec les filtres
  getReponses(): void {
    let url = 'http://127.0.0.1:8000/reponses';
    let filters: string[] = [];

    // Appliquer les filtres si présents
    if (this.filtreEntreprise) {
      filters.push(`entreprise_id=${this.filtreEntreprise}`);
    }
    if (this.filtreDate) {
      filters.push(`date_reponse=${this.filtreDate}`);
    }

    // Ajouter les filtres à l'URL
    if (filters.length > 0) {
      url += `?${filters.join('&')}`;
    }

    console.log('Request URL: ', url);  // Log the URL to check

    this.http.get<any[]>(url).subscribe(
      data => {
        console.log('Data received:', data);  // Log the response data
        this.reponses = data;
      },
      error => {
        console.error('Error fetching responses:', error);  // Log any error
      }
    );
  }

  // Récupérer la liste des entreprises pour les filtres
  getEntreprises(): void {
    this.http.get<any[]>('http://127.0.0.1:8000/entreprises').subscribe(data => {
      this.entreprises = data;
    });
  }

  // Filtrer les réponses en fonction des critères (après chaque changement de filtre)
  filtrerReponses(): void {
    console.log('Filtre appliqué:');
    console.log('Entreprise Filter:', this.filtreEntreprise);
    console.log('Date Filter:', this.filtreDate);

    // Apply filters only if filtreEntreprise is not undefined or empty
    this.getReponses(); // Recharger les réponses après filtrage
  }

  // Annuler la modification
  annulerModification(): void {
    this.editingReponse = false;
    this.reponseModifiee = {}; // Réinitialiser l'objet de la réponse
  }

  // Supprimer une réponse
  supprimerReponse(reponseId: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette réponse ?')) {
      console.log('ReponseId:', reponseId); // Debugging line to check the value
      this.http.delete(`http://127.0.0.1:8000/reponses/${reponseId}`).subscribe(
        response => {
          console.log('Réponse supprimée avec succès');
          this.getReponses(); // Recharger les réponses après suppression
        },
        error => {
          console.error('Erreur lors de la suppression', error);
        }
      );
    }
  }

  // Valider une réponse
  validerReponse(reponseId: number): void {
    this.http.put(`http://127.0.0.1:8000/reponses/valider/${reponseId}`, {}).subscribe(
      () => {
        this.getReponses(); // Recharger les réponses après validation
      },
      error => {
        console.error('Erreur lors de la validation', error);
      }
    );
  }

  // Exporter les réponses en PDF (à implémenter)
  exporterEnPDF(): void {
    console.log('Exporter en PDF');
    // Vous pouvez utiliser une bibliothèque comme jsPDF pour générer un PDF
  }

  // Exporter les réponses en Excel (à implémenter)
  exporterEnExcel(): void {
    console.log('Exporter en Excel');
    // Vous pouvez utiliser une bibliothèque comme SheetJS pour générer un fichier Excel
  }
}
