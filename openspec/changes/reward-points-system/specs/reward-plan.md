## ADDED Requirements

### Requirement: Create Reward Plans with earning rules
Administrators SHALL be able to create Reward Plans defining how customers earn points.

#### Scenario: Create invoice-amount based plan
- **WHEN** an administrator creates a Reward Plan with type "Based on Invoice Amount"
- **THEN** the plan SHALL require minimum invoice amount and points per amount ratio
- **AND** the plan SHALL calculate points as `floor(grand_total / points_per_amount)`

#### Scenario: Create item-based plan
- **WHEN** an administrator creates a Reward Plan with type "Based on Item Reward Points"
- **THEN** the plan SHALL allow specifying points per item in a child table
- **AND** the plan SHALL calculate points as `sum(item_points * qty)` for matching items only

#### Scenario: Configure affiliate levels
- **WHEN** an administrator configures affiliate levels
- **THEN** the plan SHALL allow specifying percentage for each level (L1, L2, L3...)
- **AND** traversal SHALL stop when any level's percentage is 0

#### Scenario: Configure point expiration
- **WHEN** an administrator sets expiration days on a Reward Plan
- **THEN** all points awarded under this plan SHALL expire after N days from award date
- **AND** expired points SHALL be excluded from balance calculations

### Requirement: Reward Plan status management
The system SHALL respect Reward Plan active/inactive status.

#### Scenario: Inactive plan ignored
- **GIVEN** a Reward Plan with status "Inactive"
- **WHEN** a Sales Order is submitted
- **THEN** the inactive plan SHALL NOT award any points

