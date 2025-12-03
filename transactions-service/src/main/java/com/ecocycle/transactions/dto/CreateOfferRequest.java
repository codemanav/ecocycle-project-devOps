package com.ecocycle.transactions.dto;

import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

/** Data transfer object for CreateOfferRequest. */
public record CreateOfferRequest(@NotNull Long listingId, @NotNull BigDecimal offerAmount) {}
