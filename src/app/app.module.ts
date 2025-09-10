import { NgModule, isDevMode } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToastrModule } from 'ngx-toastr';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { HeaderComponent } from './header/header.component';
import { ServiceWorkerModule } from '@angular/service-worker';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { MatExpansionModule } from '@angular/material/expansion';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { LoginComponent } from './login/login.component';
import { FinancementFormComponent } from './financement-form/financement-form.component';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { SignupComponent } from './signup/signup.component';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { AdminUtilisateursComponent } from './admin-utilisateurs/admin-utilisateurs.component';
import { AdminReponsesComponent } from './admin-reponses/admin-reponses.component';
import { AdminQuestionsComponent } from './admin-questions/admin-questions.component';
import { RecommendationComponent } from './recommendation/recommendation.component';
import { ContactComponent } from './contact/contact.component';
import { CreateProjetComponent } from './create-projet/create-projet.component';
import { AdminProjetsComponent } from './admin-projets/admin-projets.component';
import { SuiviProjetsComponent } from './suivi-projets/suivi-projets.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    HeaderComponent,
    LoginComponent,
    FinancementFormComponent,
    SignupComponent,
    AdminDashboardComponent,
    AdminUtilisateursComponent,
    AdminReponsesComponent,
    AdminQuestionsComponent,
    RecommendationComponent,
    ContactComponent,
    CreateProjetComponent,
    AdminProjetsComponent,
    SuiviProjetsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatInputModule,
    MatSelectModule,
    MatExpansionModule,
    MatButtonModule,
    MatFormFieldModule,
    MatRadioModule,
    MatCheckboxModule,
    ToastrModule.forRoot({
      positionClass: 'toast-top-right',
      preventDuplicates: true,
      progressBar: true,
      timeOut: 3000,
      closeButton: true,
    }),
    NgbModule,
    ServiceWorkerModule.register('ngsw-worker.js', {
      enabled: !isDevMode(),
      registrationStrategy: 'registerWhenStable:30000'
    })
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
