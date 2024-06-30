import { Component, Input } from '@angular/core';
import { CommonModule, DatePipe } from "@angular/common";
import { RouterModule } from '@angular/router';
import { Router } from '@angular/router';
import { DateFormatPipe } from '../../pipes/date-format.pipe';

@Component({
  selector: 'app-movie-card',
  standalone: true,
  imports: [CommonModule, RouterModule, DateFormatPipe],
  providers: [DatePipe],
  templateUrl: './movie-card.component.html',
  styleUrls: ['./movie-card.component.scss']
})
export class MovieCardComponent {
  @Input() movie: any;

  constructor(private router: Router) {}

  onImageError(event: Event) {
  }

  onImageLoad(event: Event) {
  }

  navigateToMovie(): void {
    this.router.navigate(['/movies', this.movie.name]);
  }
}
