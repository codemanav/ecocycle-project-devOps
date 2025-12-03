package com.ecocycle.marketplace.dto;

import com.ecocycle.marketplace.model.Listing;
import com.ecocycle.marketplace.model.ListingType;
import java.math.BigDecimal;

/**
 * DTO for listing information.
 *
 * @param id listing ID
 * @param title listing title
 * @param type listing type
 * @param price listing price
 * @param ownerId owner user ID
 */
public record ListingDto(Long id, String title, ListingType type, BigDecimal price, Long ownerId) {
  public static ListingDto from(Listing l) {
    return new ListingDto(l.getId(), l.getTitle(), l.getType(), l.getPrice(), l.getOwnerId());
  }
}
