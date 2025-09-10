import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminUtilisateursComponent } from './admin-utilisateurs.component';

describe('AdminUtilisateursComponent', () => {
  let component: AdminUtilisateursComponent;
  let fixture: ComponentFixture<AdminUtilisateursComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [AdminUtilisateursComponent]
    });
    fixture = TestBed.createComponent(AdminUtilisateursComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
