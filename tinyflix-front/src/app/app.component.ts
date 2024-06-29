import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { IconModule, IconSetService } from '@coreui/icons-angular';
import { MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, IconModule, MatDialogModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'tinyflix';
}
