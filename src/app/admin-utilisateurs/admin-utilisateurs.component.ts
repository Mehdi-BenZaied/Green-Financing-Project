import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray, FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../services/auth.service';
@Component({
  selector: 'app-admin-utilisateurs',
  templateUrl: './admin-utilisateurs.component.html',
  styleUrls: ['./admin-utilisateurs.component.css']
})
export class AdminUtilisateursComponent {
  utilisateurs: any[] = [];
 
  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<any[]>('http://127.0.0.1:8000/utilisateurs').subscribe({
      next: (data) => {
        this.utilisateurs = data;
      },
      error: (err) => {
        console.error("Error loading utilisateurs:", err);
      }
    });
  
  }
  supprimerUtilisateur(id: number) {
    if (confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) {
      this.http.delete(`http://127.0.0.1:8000/utilisateurs/${id}`).subscribe(() => {
        this.utilisateurs = this.utilisateurs.filter(u => u.client_id !== id);
      });
    }
  }
  }
  