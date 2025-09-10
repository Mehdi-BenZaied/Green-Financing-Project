import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AuthenticationService {
  // Example property that tracks login status
  private isLoggedIn = false;

  constructor() {}

  // Function to simulate user login
  login(): void {
    this.isLoggedIn = true;
    // Typically, you'd set some kind of token here received from your backend
  }

  // Function to simulate user logout
  logout(): void {
    this.isLoggedIn = false;
    // Clear the authentication token or user details from storage
  }

  // Check if the user is logged in
  isAuthenticated(): boolean {
    const token = localStorage.getItem('userToken');
    // Check if the token exists and is valid. This is a simplistic check.
    return !!token;
  }
}
