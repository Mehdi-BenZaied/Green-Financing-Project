import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-projet',
  templateUrl: './create-projet.component.html',
  styleUrls: ['./create-projet.component.css']
})
export class CreateProjetComponent implements OnInit {
  projetForm!: FormGroup;
  successMessage = '';
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.projetForm = this.fb.group({
      titre: ['', Validators.required],
      description: ['', Validators.required],
      montant_recherche: ['', [Validators.required, Validators.min(1)]]
    });
  }

  onSubmit(): void {
    if (this.projetForm.invalid) {
      this.errorMessage = '❌ Veuillez remplir tous les champs correctement.';
      return;
    }

    // ✅ Récupération des infos stockées dans le localStorage
    const client_id = localStorage.getItem('user_id');
    const entreprise_id = localStorage.getItem('entreprise_id');

    if (!client_id || !entreprise_id) {
      this.errorMessage = '❌ Informations manquantes pour le client ou l’entreprise.';
      return;
    }

    const projetData = {
      titre: this.projetForm.value.titre,
      description: this.projetForm.value.description,
      montant_recherche: parseFloat(this.projetForm.value.montant_recherche),
      client_id: parseInt(client_id),
      entreprise_id: parseInt(entreprise_id)
    };

    this.http.post('http://127.0.0.1:8000/projets/create', projetData).subscribe({
      next: (res: any) => {
        this.successMessage = res.message || '✅ Projet créé avec succès !';
        this.errorMessage = '';
        this.projetForm.reset();
        setTimeout(() => this.router.navigate(['/projets']), 2000); // Redirection vers une page de projets par exemple
      },
      error: (err) => {
        console.error('Erreur:', err);
        this.successMessage = '';
        this.errorMessage = err.error?.detail || '❌ Erreur lors de la création du projet.';
      }
    });
  }
}
