import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { FinancementFormComponent } from './financement-form/financement-form.component';
import { SignupComponent } from './signup/signup.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { AdminQuestionsComponent } from './admin-questions/admin-questions.component';
import { AdminUtilisateursComponent } from './admin-utilisateurs/admin-utilisateurs.component';
import { AdminReponsesComponent } from './admin-reponses/admin-reponses.component';
import { RecommendationComponent } from './recommendation/recommendation.component';
import { ContactComponent } from './contact/contact.component';
import { CreateProjetComponent } from './create-projet/create-projet.component';
import { AdminProjetsComponent } from './admin-projets/admin-projets.component';
import { SuiviProjetsComponent } from './suivi-projets/suivi-projets.component';
const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'financement-form', component: FinancementFormComponent },
  { path: 'recommendation', component: RecommendationComponent },
  { path: 'creer', component: CreateProjetComponent },
  { path: 'suivie', component: SuiviProjetsComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'admin', component: AdminDashboardComponent },
  { path: 'admin/questions', component: AdminQuestionsComponent,  },  
  { path: 'admin/utilisateurs', component: AdminUtilisateursComponent,  },  
  { path: 'admin/reponses', component: AdminReponsesComponent,  },  

  { path: 'admin/projets', component: AdminProjetsComponent },

  { path: '**', redirectTo: '', pathMatch: 'full' }  // Redirect to Home if route doesn't exist
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
