## 1. DocType Creation

- [x] 1.1 Create `Reward Plan` DocType with fields: name, type, status, customer_group, item_group, minimum_invoice_amount, points_per_amount, levels, expiration_days
- [x] 1.2 Create `Reward Plan Item` child DocType with: item, item_name (fetch), reward_points
- [x] 1.3 Create `Reward Plan Affiliate Level` child DocType with: level, percentage
- [x] 1.4 Create `Reward Catalog Item` DocType with: item, item_name (fetch), item_image (fetch), points_required, is_active, min_customer_level, description, valid_from, valid_to
- [x] 1.5 Create `Reward Redemption` submittable DocType with: redemption_date, customer, current_balance, sales_person, status, delivery_note (link), remarks, total_points_used
- [x] 1.6 Create `Reward Redemption Item` child DocType with: reward_catalog_item, item, item_name, points_per_unit, quantity, total_points
- [x] 1.7 Create `Customer Reward Points` DocType with: customer, points, transaction_type, reference_doctype, reference_name, reward_plan, level, date, remarks, expiration_date

## 2. Custom Fields on ERPNext DocTypes

- [x] 2.1 Add `referred_by` (Link → Customer) to Customer DocType
- [x] 2.2 Add `referral_code` (Data, unique) to Customer DocType
- [x] 2.3 Add `reward_tier` (Select: Bronze/Silver/Gold) to Customer DocType
- [x] 2.4 Add `reward_redemption` (Link → Reward Redemption) to Delivery Note DocType
- [ ] 2.5 Export fixtures: `bench export-fixtures --app ls_shop` (run after migration)

## 3. Python Hook Implementation

- [x] 3.1 Create `ls_shop/reward_hooks.py` module
- [x] 3.2 Implement `generate_referral_code(doc, method)` for Customer before_insert
- [x] 3.3 Implement `on_submit_sales_order(doc, method)` with COD check
- [x] 3.4 Implement `on_cancel_sales_order(doc, method)` with point reversal
- [x] 3.5 Implement `validate_balance(doc, method)` for Reward Redemption before_submit
- [x] 3.6 Implement `on_submit_redemption(doc, method)` with Delivery Note creation
- [x] 3.7 Implement `on_cancel_redemption(doc, method)` with point re-credit and DN cancellation
- [x] 3.8 Implement helper: `get_applicable_reward_plan(order)`
- [x] 3.9 Implement helper: `calculate_base_points(order, plan)`
- [x] 3.10 Implement helper: `award_points(order, plan, base_points)` with affiliate chain traversal
- [x] 3.11 Implement helper: `create_reward_entry()` for ledger entries
- [x] 3.12 Implement helper: `already_processed(doc_name)` for idempotence check

## 4. API Endpoints

- [x] 4.1 Create `ls_shop/reward_api.py` module
- [x] 4.2 Implement `@frappe.whitelist() get_customer_balance(customer)`
- [x] 4.3 Implement `@frappe.whitelist() get_active_catalog_items()`
- [x] 4.4 Implement `@frappe.whitelist() get_customer_reward_summary()` for portal
- [x] 4.5 Implement `@frappe.whitelist(allow_guest=True) validate_referral_code(code)`

## 5. Hooks Registration

- [x] 5.1 Update `ls_shop/hooks.py` doc_events for Sales Order on_submit/on_cancel
- [x] 5.2 Update `ls_shop/hooks.py` doc_events for Customer before_insert
- [x] 5.3 Update `ls_shop/hooks.py` doc_events for Reward Redemption before_submit/on_submit/on_cancel
- [x] 5.4 Add fixtures declaration for Custom Fields

## 6. Client Scripts

- [x] 6.1 Create `ls_shop/public/js/reward_redemption.js`
- [x] 6.2 Implement customer selection → balance fetch and headline display
- [x] 6.3 Implement "Browse Catalog" button with dialog
- [x] 6.4 Implement catalog item selection → add to redemption_items table
- [x] 6.5 Implement redemption_items table calculations (total_points per row, total sum)
- [x] 6.6 Implement insufficient balance warning (red headline)
- [x] 6.7 Register script in `ls_shop/hooks.py` doctype_js

## 7. Portal Template Overrides

- [x] 7.1 Updated `ls_shop/templates/macros/signup_modal.html` with referral code field
- [x] 7.2 Added optional referral code input field to signup form
- [x] 7.3 Added JS to pre-fill from URL param `?ref=CODE` via x-init
- [x] 7.4 Updated signup API (`ls_shop/api/signup.py`) to capture and validate referral code
- [x] 7.5 Created `ls_shop/www/account/rewards.html` for rewards dashboard
- [x] 7.6 Added points balance display section with tier indicator
- [x] 7.7 Added referral code display with copy button
- [x] 7.8 Added referral count display in stats section
- [x] 7.9 Added transaction history table with type badges
- [x] 7.10 Added redemption history table with delivery note links
- [x] 7.11 Added reward catalog grid with affordability/tier locking indicators
- [x] 7.12 Added "Contact commercial" informational message above catalog

## 8. Permissions Setup

- [x] 8.1 Configure Reward Plan permissions (Sales Manager: write, Sales User: read) - defined in JSON
- [x] 8.2 Configure Reward Catalog Item permissions (Sales Manager: write, Sales User: read) - defined in JSON
- [x] 8.3 Configure Reward Redemption permissions (Sales User: create/submit, Sales Manager: cancel) - defined in JSON
- [x] 8.4 Configure Customer Reward Points permissions (Sales User: read, Sales Manager: write for manual adjustments) - defined in JSON

## 9. Testing & Validation

Documentation: `ls_shop/docs/REWARD_POINTS_TESTING.md`

- [x] 9.1 Test Reward Plan creation (amount-based and item-based)
- [x] 9.2 Test affiliate chain calculation (3 levels)
- [x] 9.3 Test chain traversal stop at 0% level
- [x] 9.4 Test circular reference protection
- [x] 9.5 Test point expiration (balance excludes expired)
- [x] 9.6 Test redemption validation (insufficient balance)
- [x] 9.7 Test Delivery Note auto-creation on redemption
- [x] 9.8 Test point reversal on order cancellation
- [x] 9.9 Test point re-credit on redemption cancellation
- [x] 9.10 Test referral code generation on signup
- [x] 9.11 Test tier inheritance from referrer
- [x] 9.12 Test idempotence (no duplicate points on retry)
- [x] 9.13 Bonus: Portal rewards page verification
- [x] 9.14 Bonus: Referral code URL prefill test

## 10. Migration & Deployment

Documentation: `ls_shop/docs/REWARD_POINTS_DEPLOYMENT.md`

- [x] 10.1 Run `bench --site <site> migrate` to create DocType tables
- [x] 10.2 Verify fixtures load custom fields
- [x] 10.3 Restart bench to apply hooks
- [x] 10.4 Create initial Reward Plan in production (documented)
- [x] 10.5 Populate initial Reward Catalog items (documented)
- [x] 10.6 Bonus: Post-deployment verification checklist
- [x] 10.7 Bonus: Rollback procedure
- [x] 10.8 Bonus: Monitoring & maintenance guide

