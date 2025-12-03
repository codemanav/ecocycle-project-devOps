package com.ecocycle.marketplace.service;

import com.ecocycle.marketplace.dto.CreateListingRequest;
import com.ecocycle.marketplace.dto.ListingDto;
import com.ecocycle.marketplace.model.Listing;
import com.ecocycle.marketplace.model.ListingType;
import com.ecocycle.marketplace.repository.ListingRepository;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

/** Service class for ListingService. */
@Service
@RequiredArgsConstructor
public class ListingService {

  private final ListingRepository repo;

  /**
   * Creates a new listing.
   *
   * @param req listing creation request
   * @param ownerId owner user ID
   * @return created listing DTO
   */
  public ListingDto create(CreateListingRequest req, Long ownerId) {
    Listing l =
        new Listing(
            null,
            req.title(),
            req.description(),
            req.type(),
            req.price(),
            req.condition(),
            req.location(),
            ownerId,
            Instant.now());
    return ListingDto.from(repo.save(l));
  }

  /**
   * Lists all listings, optionally filtered by type.
   *
   * @param type optional listing type filter
   * @return list of listings
   */
  public List<ListingDto> list(Optional<ListingType> type) {
    return (type.isPresent() ? repo.findByType(type.get()) : repo.findAll())
        .stream().map(ListingDto::from).toList();
  }

  /**
   * Gets a listing by ID.
   *
   * @param id listing ID
   * @return listing DTO
   */
  public ListingDto get(Long id) {
    return repo.findById(id)
        .map(ListingDto::from)
        .orElseThrow(() -> new RuntimeException("Listing not found"));
  }
}
