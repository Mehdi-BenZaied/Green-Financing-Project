import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateProjetComponent } from './create-projet.component';

describe('CreateProjetComponent', () => {
  let component: CreateProjetComponent;
  let fixture: ComponentFixture<CreateProjetComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CreateProjetComponent]
    });
    fixture = TestBed.createComponent(CreateProjetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
