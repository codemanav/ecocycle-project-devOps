package com.ecocycle.users.service;

import com.ecocycle.users.dto.CreateUserRequest;
import com.ecocycle.users.dto.UserDto;
import com.ecocycle.users.model.User;
import com.ecocycle.users.repository.UserRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

/** Service class for UserService. */
@Service
@RequiredArgsConstructor
public class UserService {

  private final UserRepository repo;

  /** Create method. */
  public UserDto create(CreateUserRequest req) {
    User u = new User();
    u.setUsername(req.username());
    u.setEmail(req.email());
    u.setVerifier(false);
    u.setGreenScore(0);
    return UserDto.from(repo.save(u));
  }

  public List<UserDto> list() {
    return repo.findAll().stream().map(UserDto::from).toList();
  }

  /** Get method. */
  public UserDto get(Long id) {
    return repo.findById(id)
        .map(UserDto::from)
        .orElseThrow(() -> new RuntimeException("User not found"));
  }

  // this will be called by Transactions later
  /** Incrementgreenscore method. */
  public UserDto incrementGreenScore(Long id, int delta) {
    User u = repo.findById(id).orElseThrow(() -> new RuntimeException("User not found"));
    u.setGreenScore(u.getGreenScore() + delta);
    return UserDto.from(repo.save(u));
  }
}
