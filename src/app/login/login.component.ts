import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginForm: FormGroup;
  loading: boolean = false;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, this.customEmailOrAdminValidator]],
      mot_de_passe: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  // ✅ Getter raccourci pour les champs du formulaire
  get f() {
    return this.loginForm.controls;
  }

  // ✅ Validateur personnalisé pour accepter soit un email classique, soit "admin"
  customEmailOrAdminValidator(control: AbstractControl) {
    const value = control.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (value === 'admin' || emailRegex.test(value)) {
      return null;
    }
    return { invalidEmail: true };
  }

  // ✅ Fonction de connexion
  login() {
    if (this.loginForm.invalid) {
      this.errorMessage = '❌ Veuillez remplir correctement le formulaire.';
      return;
    }

    this.loading = true;
    const { email, mot_de_passe } = this.loginForm.value;

    this.authService.login({ email, mot_de_passe }).subscribe({
      next: (response) => {
        console.log('✅ Connexion réussie:', response);

        const clientId = response.user_id;

        // ✅ Stocker les infos utilisateur dans le localStorage
        localStorage.setItem('user_id', clientId);
        localStorage.setItem('nom', response.nom);
        localStorage.setItem('user_email', response.email);
        localStorage.setItem('entreprise_id', response.entreprise_id); // ✅ ajoute cette ligne
       

        // ✅ Sinon, vérifier le rôle via l'API
        this.authService.checkIfAdmin(clientId).subscribe({
          next: (res) => {
            if (res.is_admin) {
              console.log('🛡️ Admin détecté');
              this.router.navigate(['/admin']);
            } else {
              console.log('👤 Client détecté');
              this.router.navigate(['/financement-form']);
            }
          },
          error: (err) => {
            console.error('❌ Erreur lors de la vérification du rôle:', err);
            this.errorMessage = "Erreur interne lors de la détection du rôle.";
          }
        });
      },
      error: (error) => {
        console.error('❌ Erreur de connexion:', error);
        this.errorMessage = error?.error?.detail || '❌ Email ou mot de passe invalide.';
        this.loading = false;
      }
    });
  }
}
