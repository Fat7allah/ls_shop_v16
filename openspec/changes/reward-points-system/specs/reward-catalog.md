## ADDED Requirements

### Requirement: Manage reward catalog items
Sales Managers SHALL be able to configure products exchangeable for points.

#### Scenario: Add item to catalog
- **WHEN** a Sales Manager creates a Reward Catalog Item
- **THEN** they SHALL select an existing Item from inventory
- **AND** they SHALL specify points required per unit
- **AND** they SHALL set active/inactive status
- **AND** optional validity period (from/to dates) SHALL be supported

#### Scenario: Customer tier restriction
- **GIVEN** a Reward Catalog Item has Min Customer Level = "Gold"
- **WHEN** the catalog is displayed
- **THEN** only Gold tier customers SHALL see this item as available
- **AND** lower tier customers SHALL see it as locked/inaccessible

#### Scenario: Catalog item expiration
- **GIVEN** a Reward Catalog Item has Valid To date in the past
- **WHEN** the catalog is queried
- **THEN** the expired item SHALL NOT appear

#### Scenario: Item image display
- **GIVEN** a Reward Catalog Item is linked to an Item with image
- **WHEN** the catalog is displayed
- **THEN** the Item's image SHALL be shown in the catalog

