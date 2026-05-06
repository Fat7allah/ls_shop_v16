## ADDED Requirements

### Requirement: Sales person initiates redemption
Sales persons SHALL be able to create redemptions for customers, selecting items from the catalog.

#### Scenario: Create redemption
- **GIVEN** a customer has sufficient point balance
- **WHEN** a Sales Person creates a Reward Redemption
- **THEN** they SHALL select the customer
- **AND** they SHALL browse and select items from the active catalog
- **AND** the system SHALL calculate total points required
- **AND** the Sales Person SHALL be recorded as the initiator

#### Scenario: Validate sufficient balance
- **GIVEN** a customer has 500 points
- **WHEN** a redemption requiring 600 points is submitted
- **THEN** the system SHALL reject the submission
- **AND** display error: "Insufficient balance: 500 available, 600 required"

#### Scenario: Create Delivery Note on redemption submit
- **GIVEN** a valid Reward Redemption is submitted
- **WHEN** the on_submit hook executes
- **THEN** the system SHALL create a Delivery Note
- **AND** all items SHALL have rate = 0
- **AND** the Delivery Note SHALL link to the Reward Redemption
- **AND** the Delivery Note SHALL be auto-submitted

#### Scenario: Debit points on redemption
- **GIVEN** a Reward Redemption is submitted
- **WHEN** the on_submit hook executes
- **THEN** the system SHALL create a negative Customer Reward Points entry
- **AND** the entry SHALL reference the Reward Redemption

#### Scenario: Cancel redemption
- **GIVEN** a submitted Reward Redemption
- **WHEN** it is cancelled
- **THEN** the system SHALL re-credit all points to the customer
- **AND** the linked Delivery Note SHALL be cancelled
- **AND** a reversal entry SHALL be created in the ledger

#### Scenario: Idempotence on Delivery Note creation
- **GIVEN** a Reward Redemption already has a linked Delivery Note
- **WHEN** the on_submit hook triggers again
- **THEN** no new Delivery Note SHALL be created

