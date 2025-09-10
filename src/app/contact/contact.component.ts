import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent {
  contactForm: FormGroup;
  formSubmitted = false;
  formStatus: 'success' | 'error' | '' = '';

  constructor(private fb: FormBuilder) {
    this.contactForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      message: ['', Validators.required]
    });
  }

  onSubmit(): void {
    this.formSubmitted = true;
    if (this.contactForm.valid) {
      // Simuler une requête HTTP
      console.log(this.contactForm.value);
      this.formStatus = 'success';
      this.contactForm.reset();
    } else {
      this.formStatus = 'error';
    }
  }
}
