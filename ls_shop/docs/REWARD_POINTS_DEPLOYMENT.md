# Reward Points System - Deployment Guide

## Overview

This guide covers the deployment of the Reward Points System to production.

---

## Pre-Deployment Checklist

- [ ] Code committed to version control
- [ ] All tests passed in staging environment
- [ ] Backup of production database completed
- [ ] Maintenance window scheduled (if needed)
- [ ] Rollback plan prepared

---

## Task 10.1: Run Migration

### Step 1: Backup Production Database

```bash
# On production server
bench --site production.site.com backup --with-files
```

### Step 2: Pull Latest Code

```bash
cd /path/to/frappe-bench
bench get-app ls_shop
```

### Step 3: Run Migration

```bash
bench --site production.site.com migrate
```

### Expected Output:
```
Migrating production.site.com
Updating DocTypes for ls_shop
... 
Updating customizations for ls_shop
...
Migration complete
```

### Verification:
```bash
bench --site production.site.com console
```

```python
# In console
frappe.get_all("Reward Plan", limit=1)  # Should return empty list (no error)
frappe.get_all("Customer Reward Points", limit=1)  # Should work
```

---

## Task 10.2: Export Fixtures

### Step 1: Export Custom Fields

```bash
bench --site production.site.com export-fixtures --app ls_shop
```

### Step 2: Verify Fixture Files

Check that these files exist and contain data:

```bash
ls -la apps/ls_shop/ls_shop/fixtures/
```

Expected files:
- `custom_field.json` (should contain 4 entries)

### Step 3: Commit Fixtures

```bash
cd apps/ls_shop
git add ls_shop/fixtures/
git commit -m "chore: export reward points custom fields"
git push
```

---

## Task 10.3: Restart Bench

### Step 1: Restart Services

```bash
cd /path/to/frappe-bench
bench restart
```

Or for production with supervisor:

```bash
sudo supervisorctl restart frappe-bench-production:
```

### Step 2: Clear Cache

```bash
bench --site production.site.com clear-cache
bench --site production.site.com clear-website-cache
```

---

## Task 10.4: Create Initial Reward Plan

### Option A: Via Desk UI

1. Log in as Administrator or Sales Manager
2. Go to **Reward Plan** list
3. Click **New**
4. Configure:
   - **Plan Name**: "Programme de Fidélité Standard"
   - **Reward Plan Type**: "Based on Invoice Amount"
   - **Customer Group**: "All"
   - **Minimum Invoice Amount**: 100
   - **Points per Amount**: 10
   - **Levels**: 3
   - **Expiration Days**: 365
   - **Status**: Active
5. In **Affiliate Level Table**:
   | Level | Percentage |
   |-------|------------|
   | 1 | 10 |
   | 2 | 5 |
   | 3 | 2 |
6. Save and Submit

### Option B: Via API/Script

```python
import frappe

plan = frappe.new_doc("Reward Plan")
plan.plan_name = "Programme de Fidélité Standard"
plan.reward_plan_type = "Based on Invoice Amount"
plan.customer_group = "All"
plan.minimum_invoice_amount = 100
plan.points_per_amount = 10
plan.levels = 3
plan.expiration_days = 365
plan.status = "Active"

# Add affiliate levels
plan.append("affiliate_level_table", {"level": 1, "percentage": 10})
plan.append("affiliate_level_table", {"level": 2, "percentage": 5})
plan.append("affiliate_level_table", {"level": 3, "percentage": 2})

plan.insert()
plan.submit()
frappe.db.commit()
print(f"Created Reward Plan: {plan.name}")
```

Save as `create_reward_plan.py` and run:

```bash
bench --site production.site.com execute create_reward_plan.py
```

### Verification:

```bash
bench --site production.site.com console
```

```python
plans = frappe.get_all("Reward Plan", filters={"status": "Active"})
print(f"Active plans: {len(plans)}")
```

---

## Task 10.5: Populate Initial Reward Catalog

### Step 1: Create Catalog Items

Go to **Reward Catalog Item** list and add items:

#### Example Items:

| Item | Points Required | Min Level | Valid From | Valid To |
|------|-----------------|-----------|------------|----------|
| Casquette LS | 500 | Bronze | Today | +1 year |
| T-shirt Exclusif | 1000 | Bronze | Today | +1 year |
| Sac Premium | 2500 | Silver | Today | +1 year |
| Bon d'achat 100MAD | 1000 | Bronze | Today | +1 year |
| Article VIP | 5000 | Gold | Today | +1 year |

### Step 2: Bulk Import (Optional)

Create CSV file `reward_catalog.csv`:

```csv
item,points_required,min_customer_level,is_active,valid_from,valid_to,description
ITEM-001,500,Bronze,1,2026-05-06,2027-05-06,Casquette LS
ITEM-002,1000,Bronze,1,2026-05-06,2027-05-06,T-shirt Exclusif
ITEM-003,2500,Silver,1,2026-05-06,2027-05-06,Sac Premium
```

Import via:
1. Go to **Reward Catalog Item** list
2. Click **Menu** → **Import**
3. Upload CSV
4. Map fields and import

### Verification:

```python
# In console
items = frappe.get_all("Reward Catalog Item", 
    filters={"is_active": 1},
    fields=["item_name", "points_required", "min_customer_level"])
print(f"Active catalog items: {len(items)}")
for item in items:
    print(f"  - {item.item_name}: {item.points_required} pts ({item.min_customer_level})")
```

---

## Post-Deployment Verification

### 1. Check All DocTypes Exist

```bash
bench --site production.site.com console
```

```python
doctypes = [
    "Reward Plan",
    "Reward Plan Item", 
    "Reward Plan Affiliate Level",
    "Reward Catalog Item",
    "Reward Redemption",
    "Reward Redemption Item",
    "Customer Reward Points"
]

for dt in doctypes:
    meta = frappe.get_meta(dt)
    print(f"✓ {dt}: {len(meta.fields)} fields")
```

### 2. Verify Custom Fields

```python
# Check Customer fields
customer_meta = frappe.get_meta("Customer")
fields = [f.fieldname for f in customer_meta.fields]
assert "referred_by" in fields, "Missing referred_by field"
assert "referral_code" in fields, "Missing referral_code field"
assert "reward_tier" in fields, "Missing reward_tier field"
print("✓ Customer custom fields present")

# Check Delivery Note fields
dn_meta = frappe.get_meta("Delivery Note")
fields = [f.fieldname for f in dn_meta.fields]
assert "reward_redemption" in fields, "Missing reward_redemption field"
print("✓ Delivery Note custom field present")
```

### 3. Test Hooks

Create test COD Sales Order and verify:

```python
# Create test order
so = frappe.new_doc("Sales Order")
so.customer = "Test Customer"
so.transaction_date = frappe.utils.today()
so.delivery_date = frappe.utils.today()
so.custom_ecommerce_payment_mode = "COD"
so.append("items", {
    "item_code": "TEST-ITEM",
    "qty": 1,
    "rate": 500
})
so.insert()
so.submit()

# Check if points were awarded
ledger = frappe.get_all("Customer Reward Points",
    filters={"reference_name": so.name},
    fields=["customer", "points", "transaction_type"])
print(f"Ledger entries for {so.name}: {len(ledger)}")
for entry in ledger:
    print(f"  - {entry.customer}: {entry.points} ({entry.transaction_type})")
```

### 4. Verify Portal Page

1. Log in as test customer
2. Navigate to: `https://yoursite.com/en/account/rewards`
3. Verify page loads without errors

---

## Rollback Procedure

If issues occur:

### Option 1: Restore from Backup

```bash
bench --site production.site.com restore /path/to/backup.sql.gz
```

### Option 2: Disable Hooks (Quick Fix)

Edit `ls_shop/hooks.py` and comment out reward points doc_events:

```python
doc_events = {
    # ... other events ...
    # "Customer": {
    #     "before_insert": "ls_shop.reward_hooks.generate_referral_code",
    # },
    # "Sales Order": {
    #     ...
    # },
    # "Reward Redemption": {
    #     ...
    # },
}
```

Then restart:
```bash
bench restart
```

---

## Configuration Summary

### DocType Permissions (Post-Migration)

| DocType | Sales Manager | Sales User | Customer |
|---------|--------------|------------|----------|
| Reward Plan | Write | Read | - |
| Reward Catalog Item | Write | Read | - |
| Reward Redemption | Cancel | Create/Submit/Read | - |
| Customer Reward Points | Write | Read | Read (own) |

### Custom Fields Created

| DocType | Field | Type | Purpose |
|---------|-------|------|---------|
| Customer | referred_by | Link → Customer | Referral chain |
| Customer | referral_code | Data | Unique code for sharing |
| Customer | reward_tier | Select | Bronze/Silver/Gold access |
| Delivery Note | reward_redemption | Link | Track redemption source |

---

## Monitoring & Maintenance

### Daily Checks

1. Check Error Log for reward-related errors:
   - Go to **Error Log** list
   - Filter by "Reward" in error title

2. Monitor point expiration:
   ```python
   expired = frappe.get_all("Customer Reward Points",
       filters={"expiration_date": ["<", frappe.utils.today()]},
       fields=["customer", "points"])
   print(f"Expired entries: {len(expired)}")
   ```

### Monthly Tasks

1. Review Reward Plan effectiveness:
   - Total points awarded
   - Redemption rate
   - Affiliate chain depth

2. Update catalog items if needed

### Quarterly Review

1. Analyze affiliate performance
2. Adjust point values based on business metrics
3. Review tier distribution (Bronze/Silver/Gold)

---

## Support Contacts

| Issue | Contact |
|-------|---------|
| Technical issues | System Administrator |
| Business rules clarification | Sales Manager |
| Customer disputes | Customer Service |

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| System Administrator | | | |
| Sales Manager | | | |
| Project Owner | | | |

**Deployment Complete** ✓
