import { Component, Input } from '@angular/core';
import { CommonModule } from "@angular/common";
import { RouterModule } from '@angular/router';
import { Router } from '@angular/router';

@Component({
  selector: 'app-movie-card',
  standalone: true,
  imports: [CommonModule, RouterModule],
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
