## ADDED Requirements

### Requirement: Record all point transactions
The system SHALL maintain an immutable ledger of all point transactions.

#### Scenario: Record direct customer award
- **WHEN** a Sales Order is submitted
- **THEN** the system SHALL create a Customer Reward Points entry
- **AND** the entry SHALL have positive points (credit)
- **AND** the entry SHALL reference the Sales Order
- **AND** the entry SHALL record level = 0 (direct customer)
- **AND** the entry SHALL set expiration date based on Reward Plan

#### Scenario: Record affiliate award
- **WHEN** a Sales Order triggers affiliate rewards
- **THEN** the system SHALL create a Customer Reward Points entry for each affiliate
- **AND** entries SHALL have positive points (credit)
- **AND** entries SHALL record level = 1, 2, 3... (affiliate level)
- **AND** entries SHALL reference the same Sales Order

#### Scenario: Record redemption debit
- **WHEN** a Reward Redemption is submitted
- **THEN** the system SHALL create a Customer Reward Points entry
- **AND** the entry SHALL have negative points (debit)
- **AND** the entry SHALL reference the Reward Redemption
- **AND** the entry SHALL NOT have an expiration date (debits don't expire)

#### Scenario: Record redemption reversal
- **WHEN** a Reward Redemption is cancelled
- **THEN** the system SHALL create a Customer Reward Points entry
- **AND** the entry SHALL have positive points (re-credit)
- **AND** the entry SHALL reference the cancelled Reward Redemption
- **AND** the transaction type SHALL be "Redemption Reversal"

#### Scenario: Record order cancellation reversal
- **GIVEN** a Sales Order that awarded points
- **WHEN** the Sales Order is cancelled
- **THEN** the system SHALL create negative entries for all related point awards
- **AND** the transaction type SHALL be "Order Cancellation Reversal"

### Requirement: Calculate available balance
The system SHALL calculate customer balance as sum of non-expired points.

#### Scenario: Exclude expired points
- **GIVEN** a customer has 500 points expiring tomorrow
- **AND** 300 points already expired yesterday
- **WHEN** balance is calculated after tomorrow
- **THEN** the available balance SHALL be 0 (all points expired)
- **AND** expired point entries SHALL remain in ledger for audit

### Requirement: Idempotence protection
The system SHALL prevent duplicate point awards for the same transaction.

#### Scenario: Prevent duplicate Sales Order processing
- **GIVEN** a Sales Order already has Customer Reward Points entries
- **WHEN** the Sales Order submission hook triggers again (retry/error)
- **THEN** the system SHALL detect existing entries
- **AND** no new points SHALL be awarded
- **AND** the event SHALL be logged

