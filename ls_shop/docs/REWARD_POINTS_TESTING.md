# Reward Points System - Testing Guide

## Pre-requisites

Before testing, ensure:
- [ ] ERPNext v15 is installed and running
- [ ] `ls_shop` app is installed on the site
- [ ] Migration has been run to create DocType tables
- [ ] Fixtures have been loaded (custom fields created)
- [ ] At least 3 test customers exist for affiliate chain testing
- [ ] Test items exist in the system

---

## Test 9.1: Reward Plan Creation (Amount-Based)

### Steps:
1. Go to **Reward Plan** list
2. Click **New**
3. Configure:
   - Plan Name: "Standard Rewards"
   - Reward Plan Type: "Based on Invoice Amount"
   - Customer Group: "All"
   - Minimum Invoice Amount: 100
   - Points per Amount: 10 (1 point per 10 MAD)
   - Levels: 3
   - Expiration Days: 365
   - Status: Active
4. In Affiliate Level Table, add:
   - Level 1: 10%
   - Level 2: 5%
   - Level 3: 2%
5. Save and Submit

### Expected Result:
- Plan saves successfully
- Status shows "Active"

---

## Test 9.2: Reward Plan Creation (Item-Based)

### Steps:
1. Go to **Reward Plan** list
2. Click **New**
3. Configure:
   - Plan Name: "Product Rewards"
   - Reward Plan Type: "Based on Item Reward Points"
   - Customer Group: "All"
   - Levels: 2
   - Expiration Days: 180
   - Status: Active
4. In Item Reward Points table, add 2-3 items with specific point values
5. Save and Submit

### Expected Result:
- Plan saves with item-specific points

---

## Test 9.3: Affiliate Chain Calculation (3 Levels)

### Setup:
1. Create Customer A (Grandparent referrer)
2. Create Customer B, set Referred By = Customer A
3. Create Customer C, set Referred By = Customer B
4. Create Customer D, set Referred By = Customer C

### Test:
1. Create COD Sales Order for Customer D with total = 500 MAD
2. Submit the Sales Order

### Expected Result:
- Customer D (Level 0): 50 points (500/10)
- Customer C (Level 1): 5 points (50 × 10%)
- Customer B (Level 2): 2.5 → 2 points (50 × 5%, floor)
- Customer A (Level 3): 1 point (50 × 2%, floor)

Verify in **Customer Reward Points** ledger.

---

## Test 9.4: Chain Traversal Stop at 0%

### Setup:
Modify the "Standard Rewards" plan:
- Set Level 2 percentage to 0%

### Test:
Create COD Sales Order for Customer D again (500 MAD)

### Expected Result:
- Customer D: 50 points
- Customer C: 5 points (Level 1)
- Customer B: 0 points (Level 2 = 0%, **traversal stops**)
- Customer A: **No points awarded** (chain stopped)

---

## Test 9.5: Circular Reference Protection

### Setup:
Try to create circular reference:
1. Edit Customer A
2. Set Referred By = Customer D (would create A→B→C→D→A loop)

### Expected Result:
- Either validation error prevents save, OR
- Points award logic detects and prevents infinite loop

---

## Test 9.6: Point Expiration

### Setup:
1. Create Reward Plan with Expiration Days = 1 (for quick test)
2. Create Sales Order and submit (awards points)
3. Wait 2 days OR manually edit the ledger entry to set expiration_date to yesterday

### Test:
Check customer balance via:
```python
from ls_shop.reward_hooks import get_customer_balance
print(get_customer_balance("Customer Name"))
```

### Expected Result:
- Balance excludes expired points
- Ledger entry still exists but not counted

---

## Test 9.7: Redemption Validation (Insufficient Balance)

### Setup:
1. Find customer with low balance (e.g., 10 points)
2. Create Reward Catalog Item requiring 100 points
3. Go to **Reward Redemption**, select customer

### Test:
Try to add the 100-point item and submit

### Expected Result:
- **Before Submit**: Headline shows warning in red
- **On Submit**: Error message: "Solde insuffisant..."
- Document cannot be submitted

---

## Test 9.8: Delivery Note Auto-Creation on Redemption

### Setup:
1. Customer has 200 points
2. Create Reward Catalog Item: 50 points
3. Create Reward Redemption for customer, add 2 items (100 points total)

### Test:
Submit the Reward Redemption

### Expected Result:
- Redemption submitted successfully
- **Delivery Note** auto-created with:
  - Customer = redemption customer
  - Items at 0 rate
  - Reference to Reward Redemption
- Customer balance reduced by 100 points

---

## Test 9.9: Point Reversal on Order Cancellation

### Setup:
1. Create and submit COD Sales Order (awards points)
2. Note the points awarded in ledger
3. Cancel the Sales Order

### Test:
Check Customer Reward Points ledger

### Expected Result:
- New ledger entries created:
  - Negative points for all recipients
  - Transaction Type: "Order Cancellation Reversal"
  - Remarks reference the cancelled order
- Customer balances restored

---

## Test 9.10: Point Re-credit on Redemption Cancellation

### Setup:
1. Create and submit Reward Redemption (debits points, creates DN)
2. Note customer balance
3. Cancel the Reward Redemption

### Test:
Check Customer Reward Points ledger

### Expected Result:
- New ledger entry:
  - Positive points equal to redemption amount
  - Transaction Type: "Redemption Reversal"
- Delivery Note cancelled
- Customer balance restored

---

## Test 9.11: Referral Code Generation on Signup

### Test:
1. Go to website signup page
2. Register new user with email
3. Complete OTP verification

### Expected Result:
- New Customer created
- **Referral Code** field auto-populated (format: REF-XXXXXXXX)
- **Reward Tier** set to "Bronze"

Verify: Go to Customer record, check custom fields.

---

## Test 9.12: Tier Inheritance from Referrer

### Setup:
1. Find/create Customer with tier = "Gold"
2. Note their Referral Code

### Test:
1. Sign up new user
2. Enter the Gold customer's referral code during signup
3. Complete registration

### Expected Result:
- New Customer created
- **Referred By** = Gold customer
- **Reward Tier** = "Gold" (inherited from referrer)

---

## Test 9.13: Idempotence (No Duplicate Points)

### Setup:
1. Create COD Sales Order
2. Submit it (points awarded)
3. Note the ledger entries

### Test:
Simulate retry scenario:
```python
from ls_shop.reward_hooks import on_submit_sales_order
so = frappe.get_doc("Sales Order", "SAL-ORD-XXXXX")
on_submit_sales_order(so, None)  # Manually call again
```

### Expected Result:
- **No new ledger entries created**
- Log entry: "Reward points already processed for SAL-ORD-XXXXX"

---

## Test 9.14: Portal Rewards Page

### Setup:
Log in as customer with points history

### Test:
1. Navigate to `/en/account/rewards`

### Expected Result:
- Page loads without errors
- Shows:
  - Current point balance
  - Referral code with copy button
  - Transaction history table
  - Redemption history
  - Reward catalog with affordability indicators

---

## Test 9.15: Referral Code URL Prefill

### Test:
1. Visit website with URL: `https://yoursite.com/en?ref=REF-ABC12345`
2. Click "Sign Up"

### Expected Result:
- Signup modal opens
- Referral Code field pre-filled with "REF-ABC12345"

---

## Quick Verification Commands

### Check Customer Balance:
```python
from ls_shop.reward_api import get_customer_balance
result = get_customer_balance("Customer Name")
print(result)
```

### Get Customer Summary:
```python
frappe.session.user = "customer@example.com"  # Set as customer user
from ls_shop.reward_api import get_customer_reward_summary
result = get_customer_reward_summary()
print(result)
```

### Validate Referral Code:
```python
from ls_shop.reward_api import validate_referral_code
result = validate_referral_code("REF-ABC12345")
print(result)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Hooks not firing | Check `hooks.py` doc_events registration, restart bench |
| Custom fields missing | Run `bench export-fixtures` and migrate |
| API returns 403 | Check user permissions, whitelist decorators |
| Points not calculating | Check Reward Plan status = Active, customer group match |
| Catalog not loading | Check item validity dates, is_active = 1 |
| Referral code not generating | Check `before_insert` hook on Customer |

---

## Sign-off Checklist

- [ ] All 15 tests passed
- [ ] No errors in Error Log
- [ ] Customer portal displays correctly
- [ ] Sales team trained on Redemption process
- [ ] Documentation distributed
