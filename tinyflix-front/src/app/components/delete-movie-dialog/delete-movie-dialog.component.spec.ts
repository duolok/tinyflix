import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteMovieDialogComponent } from './delete-movie-dialog.component';

describe('DeleteMovieDialogComponent', () => {
  let component: DeleteMovieDialogComponent;
  let fixture: ComponentFixture<DeleteMovieDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeleteMovieDialogComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DeleteMovieDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
