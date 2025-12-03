package com.ecocycle.transactions.controller;

import com.ecocycle.transactions.dto.ClaimDonationRequest;
import com.ecocycle.transactions.dto.CreateOfferRequest;
import com.ecocycle.transactions.dto.TransactionDto;
import com.ecocycle.transactions.dto.UpdateTransactionStatusRequest;
import com.ecocycle.transactions.service.TransactionService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** REST controller for TransactionController. */
@RestController
@RequestMapping("/transactions")
@RequiredArgsConstructor
public class TransactionController {

  private final TransactionService service;

  /**
   * Creates a new offer transaction.
   *
   * @param req offer request
   * @param request HTTP request
   * @return transaction DTO
   */
  @PostMapping("/offer")
  public ResponseEntity<TransactionDto> offer(
      @Valid @RequestBody CreateOfferRequest req, HttpServletRequest request) {
    Long buyerId = (Long) request.getAttribute("userId");
    String token = request.getHeader("Authorization").substring(7);
    return ResponseEntity.status(HttpStatus.CREATED).body(service.createOffer(req, buyerId, token));
  }

  /**
   * Claims a donation.
   *
   * @param req donation request
   * @param request HTTP request
   * @return transaction DTO
   */
  @PostMapping("/donate")
  public ResponseEntity<TransactionDto> donate(
      @Valid @RequestBody ClaimDonationRequest req, HttpServletRequest request) {
    Long buyerId = (Long) request.getAttribute("userId");
    String token = request.getHeader("Authorization").substring(7);
    return ResponseEntity.status(HttpStatus.CREATED)
        .body(service.claimDonation(req, buyerId, token));
  }

  /**
   * Gets a transaction by ID.
   *
   * @param id transaction ID
   * @return transaction DTO
   */
  @GetMapping("/{id}")
  public TransactionDto get(@PathVariable Long id) {
    return service.get(id);
  }

  /**
   * Updates a transaction status.
   *
   * @param id transaction ID
   * @param req update request
   * @return updated transaction DTO
   */
  @PutMapping("/{id}")
  public TransactionDto update(
      @PathVariable Long id, @Valid @RequestBody UpdateTransactionStatusRequest req) {
    return service.updateStatus(id, req);
  }
}
