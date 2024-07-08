import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router } from "@angular/router";
import { ToastrService } from "ngx-toastr";
import { LoginService } from "../../services/login.service";
import { AuthService } from "../../services/auth.service";
import { RoleService } from "../../services/role.service";

@Component({
  selector: "app-nav-bar",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./nav-bar.component.html",
  styleUrl: "./nav-bar.component.scss",
})
export class NavBarComponent {
  isAdmin: boolean = false;

  constructor(public router: Router, private authService: AuthService, private roleService: RoleService) {}

  ngOnInit(): void {
    this.authService.getUserRole().then(() => {
      this.isAdmin = this.roleService.isAdmin();
    }).catch(error => {
        console.error('Error fetching user role:', error);
      });
  }

  onLogoutClick(): void {
    localStorage.clear();
    this.router.navigate(["/login"]);
  }
}
