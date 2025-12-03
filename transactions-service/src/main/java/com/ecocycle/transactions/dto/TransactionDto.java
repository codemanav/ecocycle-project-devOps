package com.ecocycle.transactions.dto;

import com.ecocycle.transactions.model.Transaction;
import com.ecocycle.transactions.model.TransactionStatus;
import java.math.BigDecimal;

/** Data transfer object for TransactionDto. */
public record TransactionDto(
    Long id,
    Long listingId,
    Long buyerId,
    Long sellerId,
    TransactionStatus status,
    BigDecimal agreedPrice) {
  /**
   * Converts a Transaction entity to DTO.
   *
   * @param t transaction entity
   * @return transaction DTO
   */
  public static TransactionDto from(Transaction t) {
    return new TransactionDto(
        t.getId(),
        t.getListingId(),
        t.getBuyerId(),
        t.getSellerId(),
        t.getStatus(),
        t.getAgreedPrice());
  }
}
