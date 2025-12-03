package com.ecocycle.users.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

/**
 * Data transfer object for creating a new user.
 *
 * @param username user's username
 * @param email user's email address
 */
public record CreateUserRequest(@NotBlank String username, @Email String email) {}
