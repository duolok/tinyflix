import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router } from "@angular/router";
import { ToastrService } from "ngx-toastr";
import { LoginService } from "../../services/login.service";

@Component({
  selector: "app-nav-bar",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./nav-bar.component.html",
  styleUrl: "./nav-bar.component.scss",
})
export class NavBarComponent {
  public role: string = "admin";

  constructor(public router: Router) {}

  ngOnInit(): void {}

  onLogoutClick(): void {
    localStorage.clear();
    this.router.navigate(["/"]);
  }

}
