import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-financement-form',
  templateUrl: './financement-form.component.html',
  styleUrls: ['./financement-form.component.css']
})
export class FinancementFormComponent implements OnInit {
  financementForm: FormGroup = this.fb.group({});
  userName: string = '';
  questions: any[] = [];
  groupes: any[] = [];
  errorMessage: string = '';
  hasRecommendation: boolean = false;
  hasProjet: boolean = false;
  showRedirectMessage: boolean = false;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.userName = localStorage.getItem('nom') || 'Utilisateur';
    const clientId = parseInt(localStorage.getItem('client_id') || '1');
    this.checkRecommendation(clientId);
    this.checkProjectExists(clientId);
    this.loadQuestions();
  }

  checkRecommendation(clientId: number) {
    this.http.get<any>(`http://127.0.0.1:8000/check_recommendation/${clientId}`)
      .subscribe(res => this.hasRecommendation = res.exists);
  }

  checkProjectExists(clientId: number) {
    this.http.get<any>(`http://127.0.0.1:8000/projets/exists/${clientId}`)
      .subscribe(res => this.hasProjet = res.exists);
  }

  loadQuestions() {
    this.http.get<any[]>('http://127.0.0.1:8000/questions').subscribe(data => {
      const grouped = new Map<string, any[]>();

      data.forEach(q => {
        q.visible = true;
        if ([1141, 1142].includes(q.question_id)) q.visible = false;

        const ctrlName = 'question_' + q.question_id;
        const otherCtrlName = 'Autre' + q.question_id;

        if (q.type_question === 'choix_multiple') {
          this.financementForm.addControl(ctrlName, this.fb.control([]));
        } else {
          this.financementForm.addControl(ctrlName, new FormControl('', Validators.required));
        }

        this.financementForm.addControl(otherCtrlName, new FormControl(''));

        const groupName = q.groupe || 'Autre';
        if (!grouped.has(groupName)) grouped.set(groupName, []);
        grouped.get(groupName)?.push(q);
      });

      this.questions = this.sortQuestions(data);
      this.groupes = Array.from(grouped.entries()).map(([nom, questions]) => ({ nom, questions }));
      this.setupDynamicVisibility();
    });
  }

  setupDynamicVisibility() {
    const control114 = this.financementForm.get('question_114');
    const control1141 = this.financementForm.get('question_1141');
    const control1142 = this.financementForm.get('question_1142');

    if (control114) {
      control114.valueChanges.subscribe(value => {
        const showSub = value === 'oui';
        const q1141 = this.questions.find(q => q.question_id === 1141);
        const q1142 = this.questions.find(q => q.question_id === 1142);
        if (q1141) q1141.visible = showSub;
        if (q1142) q1142.visible = showSub && !!control1141?.value;
      });
    }

    if (control1141) {
      control1141.valueChanges.subscribe(value => {
        const q1142 = this.questions.find(q => q.question_id === 1142);
        const val114 = this.financementForm.get('question_114')?.value;
        if (q1142) q1142.visible = val114 === 'oui' && !!value;
      });
    }
  }

  onCheckboxChange(event: any, questionId: number, option: string) {
    const control = this.financementForm.get('question_' + questionId) as FormControl;
    let selected: string[] = control.value || [];

    if (event.target.checked) {
      if (!selected.includes(option)) selected.push(option);
    } else {
      selected = selected.filter(v => v !== option);
    }

    control.setValue(selected);
  }

  isChecked(questionId: number, option: string): boolean {
    const val = this.financementForm.get('question_' + questionId)?.value || [];
    return val.includes(option);
  }

  validateForm(): boolean {
    this.errorMessage = '';
    let isValid = true;

    for (let q of this.questions) {
      if (!q.visible) continue;

      const ctrlVal = this.financementForm.get('question_' + q.question_id)?.value;
      const autreVal = this.financementForm.get('Autre' + q.question_id)?.value;

      if (!ctrlVal || (Array.isArray(ctrlVal) && ctrlVal.length === 0)) {
        isValid = false;
        this.errorMessage = '❌ Veuillez répondre à toutes les questions.';
        break;
      }

      if (Array.isArray(ctrlVal) && ctrlVal.includes('Autre') && !autreVal) {
        isValid = false;
        this.errorMessage = '❌ Merci de préciser votre réponse "Autre".';
        break;
      }
    }

    return isValid;
  }

  prepareAnswers() {
    const clientId = parseInt(localStorage.getItem('client_id') || '1');
    const answers: { client_id: number, question_id: number, reponse_texte: string }[] = [];

    this.questions.forEach(q => {
      const ctrl = this.financementForm.get('question_' + q.question_id)?.value;
      const autre = this.financementForm.get('Autre' + q.question_id)?.value;

      if (ctrl) {
        if (Array.isArray(ctrl)) {
          ctrl.forEach((v: string) => {
            answers.push({
              client_id: clientId,
              question_id: q.question_id,
              reponse_texte: v === 'Autre' ? autre : v
            });
          });
        } else {
          answers.push({
            client_id: clientId,
            question_id: q.question_id,
            reponse_texte: ctrl === 'Autre' ? autre : ctrl
          });
        }
      }
    });

    return answers;
  }

  onSubmit(): void {
    if (!this.validateForm()) {
      alert(this.errorMessage);
      return;
    }

    const answers = this.prepareAnswers();

    this.authService.submitAnswers(answers).subscribe(
      () => {
        alert('✅ Merci pour vos réponses. Votre recommandation est en cours...');
        this.showRedirectMessage = true;
        setTimeout(() => this.router.navigate(['/recommendation']), 5000);
      },
      error => {
        console.error('Erreur de soumission:', error);
        alert('❌ Une erreur est survenue lors de la soumission.');
      }
    );
  }

  viewRecommendation() {
    this.router.navigate(['/recommendation']);
  }

  fillNewForm() {
    this.hasRecommendation = false;
    this.financementForm.reset();
    this.questions.forEach(q => {
      this.financementForm.get('question_' + q.question_id)?.setValue('');
      this.financementForm.get('Autre' + q.question_id)?.setValue('');
    });
  }

  navigateToCreateProject() {
    this.router.navigate(['/create-projet']);
  }

  navigateToHome() {
    this.router.navigate(['/home']);
  }

  logout() {
    this.router.navigate(['/home']);
  }

  sortQuestions(questions: any[]) {
    return questions.sort((a, b) => {
      const order = [111, 112, 113, 114, 1141, 1142];
      const aIndex = order.indexOf(a.question_id);
      const bIndex = order.indexOf(b.question_id);
      if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
      if (aIndex !== -1) return -1;
      if (bIndex !== -1) return 1;
      return a.question_id - b.question_id;
    });
  }
}
