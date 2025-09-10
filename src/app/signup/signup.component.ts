import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router'; // Import Router for navigation

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent implements OnInit {
  signupForm: FormGroup;
  entreprises: any[] = [];
  errorMessage: string = '';

  constructor(private fb: FormBuilder, private http: HttpClient, private router: Router) {
    this.signupForm = this.fb.group({
      nom: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      telephone: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(15)]],
      entreprise_id: [''],
      nouvelle_entreprise: [''],
      secteur_name: [''],
      taille: [''],
      chiffre_affaires: [''],
      localisation: [''],
      mot_de_passe: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  ngOnInit() {
    this.getEntreprises();
  }

  // Fetch the list of entreprises from the API
  getEntreprises() {
    this.http.get<any[]>('http://127.0.0.1:8000/entreprises/')
      .subscribe(
        data => this.entreprises = data,
        error => console.error("Erreur de récupération des entreprises", error)
      );
  }

  // Handle when the enterprise is changed or 'new' is selected
  onEnterpriseChange() {
    const selectedEnterprise = this.signupForm.get('entreprise_id')?.value;
    if (selectedEnterprise === 'new') {
      // Clear fields for new enterprise
      this.signupForm.patchValue({
        nouvelle_entreprise: '',
        secteur_name: '',
        taille: '',
        chiffre_affaires: '',
        localisation: ''
      });
    }
  }

  // Handle the form submission
  onSubmit() {
    if (this.signupForm.invalid) {
      return;
    }

    const formData = this.signupForm.value;

    // If 'new' option for entreprise_id is selected, set entreprise_id to null for new enterprise
    if (formData.entreprise_id === 'new') {
      formData.entreprise_id = null;
    }

    // Call the API to register the user
    this.http.post('http://127.0.0.1:8000/register/', formData)
      .subscribe(
        response => {
          console.log("Inscription réussie !", response);

          // Redirect to login page after successful signup
          this.router.navigate(['/login']);
        },
        error => {
          this.errorMessage = error.error.detail;
          console.error("Erreur lors de l'inscription", this.errorMessage);
        }
      );
  }

  // Get form controls for validation
  get f() {
    return this.signupForm.controls;
  }
}
