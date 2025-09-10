import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-admin-questions',
  templateUrl: './admin-questions.component.html',
  styleUrls: ['./admin-questions.component.css']
})
export class AdminQuestionsComponent implements OnInit {
  questions: any[] = [];
  nouvelleQuestion: any = { texte: '', type_question: 'texte_libre', options: [] };
  editing = false;
  questionEnCours: any = null;
  apiUrl = 'http://127.0.0.1:8000/questions';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.chargerQuestions();
  }

  // 🔹 Charger toutes les questions
  chargerQuestions() {
    this.http.get<any[]>(this.apiUrl).subscribe(
      (data) => {
        this.questions = data;
      },
      (error) => {
        console.error('❌ Erreur de chargement:', error);
      }
    );
  }

  // 🔹 Ajouter une nouvelle question
  ajouterQuestion() {
    const newQuestion = { ...this.nouvelleQuestion };
    
    if (newQuestion.type_question === 'choix_multiple' || newQuestion.type_question === 'choix_binaire') {
      newQuestion.options = [...this.nouvelleQuestion.options];
    } else {
      newQuestion.options = []; // Pas d'options pour 'texte_libre'
    }

    this.http.post(this.apiUrl, newQuestion).subscribe(
      (response) => {
        console.log('✅ Question ajoutée:', response);
        this.chargerQuestions();
        this.nouvelleQuestion = { texte: '', type_question: 'texte_libre', options: [] }; // Réinitialiser le formulaire
      },
      (error) => {
        console.error('❌ Erreur lors de l’ajout:', error);
      }
    );
  }

  // 🔹 Supprimer une question
  supprimerQuestion(question_id: number) {
    if (confirm("⚠️ Voulez-vous vraiment supprimer cette question ?")) {
      this.http.delete(`${this.apiUrl}/${question_id}`).subscribe(
        (response) => {
          console.log('✅ Question supprimée:', response);
          this.chargerQuestions();
        },
        (error) => {
          console.error('❌ Erreur lors de la suppression:', error);
        }
      );
    }
  }

  // 🔹 Préparer la modification d'une question
  remplirFormulaire(question: any) {
    this.nouvelleQuestion = { ...question };
    this.editing = true;
    this.questionEnCours = question;
  }

  // 🔹 Modifier une question
  modifierQuestion() {
    if (!this.nouvelleQuestion.question_id) return;
  
    const updatedQuestion = { ...this.nouvelleQuestion };

    if (updatedQuestion.type_question !== 'choix_multiple' && updatedQuestion.type_question !== 'choix_binaire') {
      updatedQuestion.options = []; // Supprimer les options si le type change
    }

    this.http.put(`${this.apiUrl}/${updatedQuestion.question_id}`, updatedQuestion)
      .subscribe(
        (response) => {
          console.log('✅ Question mise à jour:', response);
          this.chargerQuestions();
          this.annulerModification();
        },
        (error) => {
          console.error("❌ Erreur lors de la mise à jour:", error);
        }
      );
  }

  // 🔹 Annuler la modification
  annulerModification() {
    this.nouvelleQuestion = { texte: '', type_question: 'texte_libre', options: [] };
    this.editing = false;
    this.questionEnCours = null;
  }

  // 🔹 Ajouter une option pour 'choix_multiple' ou 'choix_binaire'
  ajouterOption() {
    if (!this.nouvelleQuestion.options) {
      this.nouvelleQuestion.options = [];
    }
    this.nouvelleQuestion.options.push('');
  }

  // 🔹 Supprimer une option
  supprimerOption(index: number) {
    this.nouvelleQuestion.options.splice(index, 1);
  }
}
