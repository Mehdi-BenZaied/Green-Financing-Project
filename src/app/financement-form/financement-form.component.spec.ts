import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FinancementFormComponent } from './financement-form.component';

describe('FinancementFormComponent', () => {
  let component: FinancementFormComponent;
  let fixture: ComponentFixture<FinancementFormComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [FinancementFormComponent]
    });
    fixture = TestBed.createComponent(FinancementFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
