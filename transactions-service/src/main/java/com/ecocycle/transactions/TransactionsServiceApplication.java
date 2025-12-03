package com.ecocycle.transactions;

import com.ecocycle.transactions.model.Transaction;
import com.ecocycle.transactions.model.TransactionStatus;
import com.ecocycle.transactions.repository.TransactionRepository;
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
    scanBasePackages = {"com.ecocycle.transactions", "com.ecocycle.common.security"})
@OpenAPIDefinition(
    info =
        @Info(
            title = "EcoCycle Transactions Service",
            version = "1.0",
            description = "APIs for managing transactions in EcoCycle"))
public class TransactionsServiceApplication {

  public static void main(String[] args) {
    SpringApplication.run(TransactionsServiceApplication.class, args);
  }

  /**
   * Seed the transactions database with a couple of demo records if it's empty.
   *
   * <p>This helps the frontend demo: you can safely call GET /transactions/1 and /transactions/2.
   */
  @Bean
  CommandLineRunner seedTransactions(TransactionRepository repo) {
    return args -> {
      if (repo.count() > 0) {
        return;
      }

      Transaction tx1 =
          new Transaction(
              null,
              100L, // listingId (demo value)
              1L, // buyerId
              2L, // sellerId
              TransactionStatus.PENDING,
              new BigDecimal("25.00"),
              Instant.now(),
              Instant.now());

      Transaction tx2 =
          new Transaction(
              null,
              101L,
              3L,
              4L,
              TransactionStatus.CONFIRMED,
              new BigDecimal("0.00"),
              Instant.now(),
              Instant.now());

      repo.save(tx1);
      repo.save(tx2);
    };
  }
}
