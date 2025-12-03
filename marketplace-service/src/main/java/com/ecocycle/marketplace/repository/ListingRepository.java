package com.ecocycle.marketplace.repository;

import com.ecocycle.marketplace.model.Listing;
import com.ecocycle.marketplace.model.ListingType;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

/** Repository interface for ListingRepository. */
public interface ListingRepository extends JpaRepository<Listing, Long> {
  List<Listing> findByType(ListingType type);
}
