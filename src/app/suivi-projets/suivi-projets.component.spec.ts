import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SuiviProjetsComponent } from './suivi-projets.component';

describe('SuiviProjetsComponent', () => {
  let component: SuiviProjetsComponent;
  let fixture: ComponentFixture<SuiviProjetsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SuiviProjetsComponent]
    });
    fixture = TestBed.createComponent(SuiviProjetsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
