import { Component, OnInit } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { NavBarComponent } from "../../components/nav-bar/nav-bar.component";
import { MovieCardComponent } from '../../components/movie-card/movie-card.component';
import { CommonModule } from "@angular/common";
import { Router } from '@angular/router';
import { SubscriptionService } from '../../services/subscription.service';
import { FormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { UnsubscribeDialogComponent } from '../../components/unsubscribe-dialog/unsubscribe-dialog.component';

@Component({
  selector: 'app-subscriptions',
  standalone: true,
  imports: [CommonModule, NavBarComponent, MatIconModule, MovieCardComponent, FormsModule],
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.scss']
})
export class SubscriptionsComponent implements OnInit {
  genres: string[] = [];
  actors: string[] = [];
  directors: string[] = [];
  searchQuery: string = '';

  constructor(
    private router: Router,
    private subscriptionService: SubscriptionService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadSubscriptions();
  }

  loadSubscriptions() {
    this.subscriptionService.getSubscriptions().subscribe(
      response => {
        console.log('Subscriptions:', response);
        const subscriptions = response.data.subscriptions;
        this.genres = subscriptions.genres || [];
        this.actors = subscriptions.actors || [];
        this.directors = subscriptions.directors || [];
      },
      error => {
        console.error('Error loading subscriptions.', error);
      }
    );
  }

  cancelSubscription(type: string, value: string) {
    const dialogRef = this.dialog.open(UnsubscribeDialogComponent, {
      data: { type, value },
      width: "40%",
      backdropClass: "backdropBackground"
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        const subscriptionCriteria = { [type]: [{ "S": value }] };
        console.log(subscriptionCriteria);
        this.subscriptionService.unsubscribe(subscriptionCriteria).subscribe(
          response => {
            console.log('Subscription cancelled:', response);
            this.loadSubscriptions(); 
          },
          error => {
            console.error('Error cancelling subscription.', error);
          }
        );
      }
    });
  }
}

