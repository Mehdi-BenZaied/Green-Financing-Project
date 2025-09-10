import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminReponsesComponent } from './admin-reponses.component';

describe('AdminReponsesComponent', () => {
  let component: AdminReponsesComponent;
  let fixture: ComponentFixture<AdminReponsesComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [AdminReponsesComponent]
    });
    fixture = TestBed.createComponent(AdminReponsesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
