## ADDED Requirements

### Requirement: Display point balance in portal
Customers SHALL see their current point balance in the account portal.

#### Scenario: View balance on account page
- **GIVEN** a logged-in customer
- **WHEN** they visit the account dashboard
- **THEN** their current available point balance SHALL be displayed prominently

#### Scenario: View transaction history
- **GIVEN** a logged-in customer
- **WHEN** they view the loyalty section
- **THEN** they SHALL see a list of recent transactions
- **AND** entries SHALL show: date, type, points (+/-), reference, remarks

#### Scenario: View redemption history
- **GIVEN** a logged-in customer
- **WHEN** they view the loyalty section
- **THEN** they SHALL see their past redemptions
- **AND** entries SHALL show: date, points used, delivery note link

#### Scenario: View reward catalog (read-only)
- **GIVEN** a logged-in customer
- **WHEN** they view the loyalty section
- **THEN** they SHALL see the active reward catalog
- **AND** affordable items SHALL be highlighted
- **AND** unaffordable items SHALL show "X points needed"
- **AND** tier-locked items SHALL indicate required tier

#### Scenario: Display referral code
- **GIVEN** a logged-in customer
- **WHEN** they view the loyalty section
- **THEN** their unique referral code SHALL be displayed
- **AND** a shareable link SHALL be provided: `https://<site>/sign-up?ref=<code>`
- **AND** a "Copy Link" button SHALL be available

#### Scenario: Display referral count
- **GIVEN** a logged-in customer with referrals
- **WHEN** they view the loyalty section
- **THEN** the count of customers they referred SHALL be displayed

#### Scenario: Contact commercial message
- **GIVEN** a logged-in customer viewing the catalog
- **WHEN** they attempt to redeem (informational only)
- **THEN** a message SHALL display: "Contact your commercial or visit store to redeem points"

