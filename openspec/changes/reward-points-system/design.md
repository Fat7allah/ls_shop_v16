## Context

`ls_shop` is a Lifestyle Ecommerce app extending ERPNext v15 with bilingual (EN/AR) support. It handles Quotation → Sales Order → Payment → Delivery Note flow with COD, Telr, and Tabby payment methods.

The Reward Points module integrates into this existing architecture without creating a separate Frappe app (to avoid circular dependencies and installation ordering issues).

---

## Goals / Non-Goals

**Goals:**
- Implement point award on COD Sales Order submission
- Build multi-level affiliate reward traversal (up the referral chain)
- Create configurable Reward Plans with per-plan expiration
- Enable sales-person managed redemptions with auto Delivery Note generation
- Add portal visibility for customers (balance, history, referral sharing)
- Capture referral codes during signup
- Reverse points on order cancellation/return

**Non-Goals:**
- Support for non-COD payment modes in initial release
- Customer self-redemption interface
- Point-to-cash conversion
- Mobile app integration
- Integration with external loyalty platforms

---

## Decisions

### 1. Hook on Sales Order (not Sales Invoice)

**Rationale:** COD orders create Sales Invoices later (often after delivery). Points should be visible immediately after order confirmation. Hooking `on_submit` on Sales Order with `custom_ecommerce_payment_mode == "COD"` check ensures timely award.

### 2. Upward Chain Traversal

```
Purchase: A places order
Referral chain (traversed upward):
  A ──referred_by──▶ B ──referred_by──▶ C ──referred_by──▶ D

Rewards:
  B = Level 1 (direct referrer of A)
  C = Level 2 (referrer of B)
  D = Level 3 (referrer of C)
```

**Stop condition:** If any level's percentage is 0, traversal halts. This prevents rewarding distant chain members when an intermediate tier is disabled.

### 3. Circular Reference Protection

```python
visited = set([purchasing_customer])
while traversing:
    if referrer in visited:
        break  # Loop detected
    visited.add(referrer)
```

**Rationale:** Malformed data (A→B→C→A) could cause infinite loops. The visited set guarantees termination.

### 4. Point Expiration per Reward Plan

Each Reward Plan defines `expiration_days`. Points awarded under that plan expire after N days. Balance calculation filters:
```sql
WHERE expiration_date > NOW() OR expiration_date IS NULL
```

**Rationale:** Different marketing campaigns may have different expiration policies.

### 5. Ledger Pattern for Customer Reward Points

Non-submittable DocType recording every transaction:
- Positive = credit (award, reversal)
- Negative = debit (redemption)
- Immutable entries (no editing, only new entries)

**Rationale:** Full audit trail, simple balance calculation via SUM(), supports time-based queries.

### 6. Reward Redemption Creates Delivery Note at 0 MAD

Sales person selects items from catalog → system creates Delivery Note with:
- `rate = 0` for all items
- `custom_reward_redemption` linked to redemption doc
- Auto-submitted on redemption submit

**Rationale:** Seamless integration with existing ERPNext inventory/shipping workflow.

### 7. Customer Level = Inherited from Referrer

On Customer creation, if `referred_by` is set:
```python
new_customer.reward_tier = referrer.reward_tier
```

**Rationale:** Creates tier-based incentive structure. If Gold members refer others, those others become Gold too.

### 8. Sales Person Assignment

Redemption.sales_person = `frappe.session.user` (converted to Sales Person link)

**Rationale:** Simple, auditable, no selection UI needed.

---

## Data Model

### DocTypes

| DocType | Type | Purpose |
|---------|------|---------|
| `Reward Plan` | Standard | Configuration: earning rules, affiliate percentages, expiration |
| `Reward Plan Item` | Child | Items with specific point values (for item-based plans) |
| `Reward Plan Affiliate Level` | Child | Percentage per affiliate level (L1, L2, L3...) |
| `Reward Catalog Item` | Standard | Products exchangeable for points |
| `Reward Redemption` | Submittable | Sales-person initiated redemption transaction |
| `Reward Redemption Item` | Child | Selected catalog items in a redemption |
| `Customer Reward Points` | Standard | Ledger: all point transactions |

### Custom Fields on ERPNext DocTypes

| DocType | Field | Type | Purpose |
|---------|-------|------|---------|
| `Customer` | `referred_by` | Link → Customer | Up-chain referral reference |
| `Customer` | `referral_code` | Data (unique) | Shareable code for down-chain |
| `Customer` | `reward_tier` | Select | Bronze/Silver/Gold |
| `Delivery Note` | `reward_redemption` | Link → Reward Redemption | Track redemption delivery |

---

## API Endpoints (Whitelist)

| Endpoint | Purpose |
|----------|---------|
| `get_customer_balance(customer)` | Current available points |
| `get_active_catalog_items()` | Reward catalog for redemption form |
| `get_customer_reward_summary()` | Portal: balance + history + catalog + redemptions |
| `validate_referral_code(code)` | Signup: check code validity |

---

## Hooks

| DocType | Event | Handler |
|---------|-------|---------|
| `Sales Order` | `on_submit` | `reward_hooks.on_submit_sales_order` |
| `Sales Order` | `on_cancel` | `reward_hooks.on_cancel_sales_order` |
| `Customer` | `before_insert` | `reward_hooks.generate_referral_code` |
| `Reward Redemption` | `before_submit` | `reward_hooks.validate_balance` |
| `Reward Redemption` | `on_submit` | `reward_hooks.create_delivery_note` |
| `Reward Redemption` | `on_cancel` | `reward_hooks.reverse_points` |

---

## File Structure

```
ls_shop/
├── hooks.py                          # Add doc_events, fixtures
├── reward_hooks.py                   # NEW: All hook handlers
├── reward_api.py                     # NEW: Whitelist endpoints
├── doctype/
│   ├── reward_plan/
│   ├── reward_plan_item/
│   ├── reward_plan_affiliate_level/
│   ├── reward_catalog_item/
│   ├── reward_redemption/
│   ├── reward_redemption_item/
│   └── customer_reward_points/
├── public/js/
│   └── reward_redemption.js          # NEW: Client script
├── templates/pages/
│   ├── sign-up.html                  # OVERRIDE: Add referral field
│   └── my-account.html               # OVERRIDE: Add points section
└── fixtures/
    └── custom_field.json             # EXPORT: Customer fields
```

---

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **Race condition on redemption** | Use `before_submit` validation + DB transaction. Balance check happens server-side at submission time, not just client-side. |
| **Sales Order cancellation after points used** | On cancel, reverse all point entries linked to this order. If customer has insufficient balance (already spent), log error and flag for manual review. |
| **Partial returns** | For simplicity: reverse full points on any return. Future enhancement: pro-rate by returned item value. |
| **Performance on large chains** | Max 10 levels configured. Traversal is O(levels) with single queries per level — negligible overhead. |
| **Duplicate point awards** | Idempotence check: skip if `Customer Reward Points` entries already exist for this Sales Order. |

---

## Open Questions

1. **Partial return handling** — Reverse full or pro-rated points? (Currently: full reversal for simplicity)
2. **Tier upgrade logic** — How does a customer's `reward_tier` change over time? (Currently: inherited once at creation)
3. **Expired points display** — Show in history as "expired" or hide completely? (Currently: include in history with status)

