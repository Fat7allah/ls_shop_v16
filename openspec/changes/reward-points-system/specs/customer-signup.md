## ADDED Requirements

### Requirement: Capture referral code during signup
New customers SHALL be able to enter a referral code during the signup process.

#### Scenario: Enter referral code in signup form
- **GIVEN** a new visitor on the signup page
- **WHEN** the signup form is displayed
- **THEN** an optional field "Referral Code" SHALL be visible
- **AND** the field SHALL accept alphanumeric codes

#### Scenario: Pre-fill from URL parameter
- **GIVEN** a visitor accesses `/sign-up?ref=ABC123`
- **WHEN** the signup form loads
- **THEN** the Referral Code field SHALL be pre-filled with "ABC123"

#### Scenario: Validate referral code
- **GIVEN** a user enters referral code "ABC123"
- **WHEN** the signup form is submitted
- **THEN** the system SHALL validate the code exists
- **AND** the code SHALL match an existing Customer's `referral_code`

#### Scenario: Invalid referral code handling
- **GIVEN** a user enters invalid referral code "INVALID"
- **WHEN** the signup form is submitted
- **THEN** the system SHALL log the invalid attempt
- **AND** the signup SHALL proceed without referral linkage
- **AND** no error SHALL be shown to user (graceful degradation)

## CHANGED Requirements

### Requirement: Create customer with referral linkage
When a new user signs up, the system SHALL create their Customer record with proper referral linkage.

#### Scenario: Link customer to referrer
- **GIVEN** a valid referral code was provided during signup
- **WHEN** the Customer is created
- **THEN** the `referred_by` field SHALL be set to the referring Customer
- **AND** the `reward_tier` field SHALL inherit from the referrer

#### Scenario: Generate unique referral code
- **GIVEN** a new Customer is being created
- **WHEN** the before_insert hook executes
- **THEN** a unique referral code SHALL be generated
- **AND** format SHALL be "REF-" + 8-char hash (uppercase)

#### Scenario: No referrer provided
- **GIVEN** no referral code was provided
- **WHEN** the Customer is created
- **THEN** `referred_by` SHALL be null
- **AND** `reward_tier` SHALL default to "Bronze"

