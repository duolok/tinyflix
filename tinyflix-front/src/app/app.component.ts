import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { IconModule, IconSetService } from '@coreui/icons-angular';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDialogModule } from '@angular/material/dialog';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, IconModule, MatDialogModule, MatDatepickerModule, MatNativeDateModule, MatInputModule, MatFormFieldModule, MatChipsModule, MatIconModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'tinyflix';
}
