package com.ecocycle.transactions.model;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** Domain model representing Transaction. */
@Entity
@Table(name = "transactions")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Transaction {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  private Long listingId;
  private Long buyerId;
  private Long sellerId;

  @Enumerated(EnumType.STRING)
  private TransactionStatus status;

  private BigDecimal agreedPrice;

  private Instant createdAt = Instant.now();
  private Instant updatedAt = Instant.now();
}
