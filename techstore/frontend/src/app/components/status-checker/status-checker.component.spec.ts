import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatusCheckerComponent } from './status-checker.component';

describe('StatusCheckerComponent', () => {
  let component: StatusCheckerComponent;
  let fixture: ComponentFixture<StatusCheckerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [StatusCheckerComponent],
    });
    fixture = TestBed.createComponent(StatusCheckerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
