package com.ecocycle.transactions.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

/** Client for external service communication. */
@Component
public class MarketplaceClient {

  private final WebClient webClient;
  private final String baseUrl;

  public MarketplaceClient(@Value("${marketplace.base-url:http://localhost:8081}") String baseUrl) {
    this.webClient = WebClient.builder().build();
    this.baseUrl = baseUrl;
  }

  /** Getlisting method. */
  public ListingDto getListing(Long id, String token) {
    return webClient
        .get()
        .uri(baseUrl + "/listings/{id}", id)
        .header("Authorization", "Bearer " + token) // ✅ add token
        .retrieve()
        .bodyToMono(ListingDto.class)
        .block();
  }
}
