package com.ecocycle.transactions.repository;

import com.ecocycle.transactions.model.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;

/** Repository interface for TransactionRepository. */
public interface TransactionRepository extends JpaRepository<Transaction, Long> {
}
