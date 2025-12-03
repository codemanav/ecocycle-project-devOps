package com.ecocycle.users.controller;

import com.ecocycle.users.dto.CreateUserRequest;
import com.ecocycle.users.dto.UserDto;
import com.ecocycle.users.service.UserService;
import jakarta.validation.Valid;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** REST controller for UserController. */
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

  private final UserService service;

  @PostMapping
  public ResponseEntity<UserDto> create(@Valid @RequestBody CreateUserRequest req) {
    return ResponseEntity.status(HttpStatus.CREATED).body(service.create(req));
  }

  @GetMapping
  public List<UserDto> list() {
    return service.list();
  }

  /**
   * Gets a user by ID.
   *
   * @param id user ID
   * @return user DTO
   */
  @GetMapping("/{id}")
  public UserDto get(@PathVariable Long id) {
    return service.get(id);
  }

  /**
   * Updates a user's green score.
   *
   * @param id user ID
   * @param delta score increment
   * @return updated user DTO
   */
  @PutMapping("/{id}/greenscore")
  public UserDto updateScore(@PathVariable Long id, @RequestParam(defaultValue = "1") int delta) {
    return service.incrementGreenScore(id, delta);
  }
}
