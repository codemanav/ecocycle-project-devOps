package com.ecocycle.transactions.dto;

import com.ecocycle.transactions.model.TransactionStatus;
import jakarta.validation.constraints.NotNull;

/** Data transfer object for UpdateTransactionStatusRequest. */
public record UpdateTransactionStatusRequest(@NotNull TransactionStatus status) {}
