package com.ecocycle.transactions.dto;

import jakarta.validation.constraints.NotNull;

/** Data transfer object for ClaimDonationRequest. */
public record ClaimDonationRequest(@NotNull Long listingId) {}
