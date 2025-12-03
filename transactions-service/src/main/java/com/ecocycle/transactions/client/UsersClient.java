package com.ecocycle.transactions.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

/** Client for external service communication. */
@Component
public class UsersClient {

  private final WebClient webClient;
  private final String baseUrl;

  public UsersClient(@Value("${users.base-url:http://localhost:8083}") String baseUrl) {
    this.webClient = WebClient.builder().build();
    this.baseUrl = baseUrl;
  }

  /** Incrementgreenscore method. */
  public void incrementGreenScore(Long userId, int delta) {
    webClient
        .put()
        .uri(baseUrl + "/users/{id}/greenscore?delta={delta}", userId, delta)
        .retrieve()
        .bodyToMono(Void.class)
        .block();
  }
}
