package com.ecocycle.marketplace.dto;

import com.ecocycle.marketplace.model.ListingType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

/**
 * Request DTO for creating a new listing.
 *
 * @param title listing title
 * @param description listing description
 * @param type listing type
 * @param price listing price
 * @param condition item condition
 * @param location item location
 */
public record CreateListingRequest(
    @NotBlank String title,
    String description,
    @NotNull ListingType type,
    BigDecimal price,
    String condition,
    String location) {}
