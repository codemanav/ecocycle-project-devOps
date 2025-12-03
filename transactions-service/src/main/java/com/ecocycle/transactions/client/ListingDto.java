package com.ecocycle.transactions.client;

import java.math.BigDecimal;

/** Client for external service communication. */
public record ListingDto(Long id, String title, String type, BigDecimal price, Long ownerId) {}
