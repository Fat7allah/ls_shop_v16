## ADDED Requirements

### Requirement: Award points on COD Sales Order submit
When a COD Sales Order is submitted, the system SHALL award points based on applicable Reward Plan.

#### Scenario: COD order triggers points
- **GIVEN** a Sales Order with `custom_ecommerce_payment_mode = "COD"`
- **WHEN** the Sales Order is submitted
- **THEN** the reward hooks SHALL execute
- **AND** points SHALL be awarded to customer and affiliates

#### Scenario: Non-COD order ignored
- **GIVEN** a Sales Order with payment mode "Telr" or "Tabby"
- **WHEN** the Sales Order is submitted
- **THEN** no points SHALL be awarded

#### Scenario: Find applicable Reward Plan
- **GIVEN** multiple Reward Plans exist
- **WHEN** a Sales Order is submitted
- **THEN** the system SHALL find the first active plan matching:
  - Customer Group (if specified, or "All")
  - Item Group (if item-based plan)

#### Scenario: Calculate base points (invoice amount)
- **GIVEN** an invoice-amount based plan
- **AND** minimum amount = 100, points_per_amount = 10 (1 pt per 10 MAD)
- **AND** order grand_total = 550
- **WHEN** points are calculated
- **THEN** base points SHALL be floor(550 / 10) = 55 points

#### Scenario: Calculate base points (item based)
- **GIVEN** an item-based plan
- **AND** Item A = 10 points, Item B = 20 points
- **AND** order has 2x Item A, 1x Item B
- **WHEN** points are calculated
- **THEN** base points SHALL be (2*10) + (1*20) = 40 points

#### Scenario: Order below minimum ignored
- **GIVEN** an invoice-amount plan with minimum = 500
- **AND** order grand_total = 300
- **WHEN** the order is submitted
- **THEN** no points SHALL be awarded

## CHANGED Requirements

### Requirement: Reverse points on Sales Order cancellation
When a Sales Order is cancelled, the system SHALL reverse all points awarded from that order.

#### Scenario: Cancel order reverses points
- **GIVEN** a submitted Sales Order that awarded points
- **WHEN** the order is cancelled
- **THEN** the on_cancel hook SHALL execute
- **AND** negative entries SHALL be created for all prior awards
- **AND** transaction type SHALL be "Order Cancellation Reversal"

#### Scenario: Handle already-spent points
- **GIVEN** a customer was awarded 500 points from an order
- **AND** the customer spent 300 points on redemption
- **AND** the remaining balance is 200
- **WHEN** the original order is cancelled
- **THEN** the system SHALL attempt to reverse 500 points
- **AND** if insufficient balance, log error for manual review

#### Scenario: Idempotence on cancellation
- **GIVEN** an order's points were already reversed
- **WHEN** cancellation hook triggers again
- **THEN** no duplicate reversal entries SHALL be created

