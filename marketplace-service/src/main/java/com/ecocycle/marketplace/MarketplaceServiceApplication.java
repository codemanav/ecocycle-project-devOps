package com.ecocycle.marketplace;

import com.ecocycle.marketplace.model.Listing;
import com.ecocycle.marketplace.model.ListingType;
import com.ecocycle.marketplace.repository.ListingRepository;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import java.math.BigDecimal;
import java.time.Instant;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

/** Spring Boot application main class. */
@SpringBootApplication(
    scanBasePackages = {"com.ecocycle.marketplace", "com.ecocycle.common.security"})
@OpenAPIDefinition(
    info =
        @Info(
            title = "EcoCycle Marketplace Service",
            version = "1.0",
            description = "APIs for managing listings in EcoCycle"))
public class MarketplaceServiceApplication {

  public static void main(String[] args) {
    SpringApplication.run(MarketplaceServiceApplication.class, args);
  }

  /**
   * Seed the marketplace database with a few demo listings if it's empty.
   *
   * <p>This makes it easy to test the frontend and other services without manual inserts.
   */
  @Bean
  CommandLineRunner seedListings(ListingRepository repo) {
    return args -> {
      if (repo.count() > 0) {
        return;
      }

      Listing saleListing =
          new Listing(
              null,
              "Eco-friendly Bike",
              "Lightly used commuter bike, great for city rides.",
              ListingType.SALE,
              new BigDecimal("120.00"),
              "Good",
              "Raleigh, NC",
              1L,
              Instant.now());

      Listing rentalListing =
          new Listing(
              null,
              "Compost Bin Rental",
              "Weekly rental for a large compost bin.",
              ListingType.RENTAL,
              new BigDecimal("10.00"),
              "Excellent",
              "Raleigh, NC",
              2L,
              Instant.now());

      Listing donationListing =
          new Listing(
              null,
              "Free Glass Jars",
              "Box of assorted glass jars for reuse.",
              ListingType.DONATION,
              BigDecimal.ZERO,
              "Fair",
              "Raleigh, NC",
              3L,
              Instant.now());

      repo.save(saleListing);
      repo.save(rentalListing);
      repo.save(donationListing);
    };
  }
}
