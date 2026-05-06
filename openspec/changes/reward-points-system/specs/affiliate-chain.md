## ADDED Requirements

### Requirement: Traverse referral chain upward
When a customer places an order, the system SHALL traverse the referral chain upward and award points at each configured level.

#### Scenario: Single-level affiliate reward
- **GIVEN** Customer A was referred by B
- **AND** the Reward Plan has Level 1 percentage = 10%
- **WHEN** A places an order earning 100 base points
- **THEN** B SHALL receive 10 points (10% of base)

#### Scenario: Multi-level affiliate reward
- **GIVEN** referral chain: D (buyer) ← C ← B ← A
- **AND** Reward Plan has Level 1 = 10%, Level 2 = 5%, Level 3 = 2%
- **WHEN** D places an order earning 1000 base points
- **THEN** C SHALL receive 100 points (Level 1)
- **AND** B SHALL receive 50 points (Level 2)
- **AND** A SHALL receive 20 points (Level 3)

#### Scenario: Chain traversal stops at zero percentage
- **GIVEN** referral chain: D (buyer) ← C ← B ← A
- **AND** Reward Plan has Level 1 = 10%, Level 2 = 0%, Level 3 = 5%
- **WHEN** D places an order
- **THEN** C SHALL receive points (Level 1)
- **AND** B SHALL NOT receive points (Level 2 is 0%)
- **AND** A SHALL NOT receive points (traversal stopped at B)

#### Scenario: Circular reference protection
- **GIVEN** malformed chain: A ← B ← C ← A (circular)
- **WHEN** A places an order
- **THEN** the system SHALL detect the loop via visited set
- **AND** traversal SHALL stop before infinite loop
- **AND** points SHALL be awarded only to valid chain members (B, C)

#### Scenario: Missing referrer ends traversal
- **GIVEN** chain: D (buyer) ← C ← B (B has no referrer)
- **AND** Reward Plan has 5 levels configured
- **WHEN** D places an order
- **THEN** C and B SHALL receive points
- **AND** traversal SHALL stop at B (no referrer)

