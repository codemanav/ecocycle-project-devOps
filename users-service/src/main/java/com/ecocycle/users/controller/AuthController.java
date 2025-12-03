package com.ecocycle.users.controller;

import com.ecocycle.users.model.User;
import com.ecocycle.users.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** REST controller for AuthController. */
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

  private final UserRepository repo;

  /**
   * Registers a new user.
   *
   * @param username user's username
   * @param email user's email
   * @return Success message
   */
  @PostMapping("/register")
  public ResponseEntity<String> register(
      @RequestParam String username, @RequestParam String email) {
    User u = new User();
    u.setUsername(username);
    u.setEmail(email);
    repo.save(u);
    return ResponseEntity.ok("User registered successfully");
  }

  /**
   * Logs in a user by email.
   *
   * @param email user's email
   * @return Success message
   */
  @PostMapping("/login")
  public ResponseEntity<String> login(@RequestParam String email) {
    User u =
        repo.findAll().stream()
            .filter(x -> x.getEmail().equals(email))
            .findFirst()
            .orElseThrow(() -> new RuntimeException("User not found"));
    return ResponseEntity.ok("User logged in successfully: " + u.getUsername());
  }
}
