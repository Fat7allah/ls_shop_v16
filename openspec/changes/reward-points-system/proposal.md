# Reward Points System with Affiliate Chain

## Summary

Build a complete **Reward Points** module integrated into `ls_shop` (Frappe/ERPNext v15). Customers accumulate points on COD orders, with multi-level affiliate rewards flowing up the referral chain. Redemptions are managed exclusively by sales persons in back-office.

---

## Motivation

- **Increase customer retention** through gamified loyalty points
- **Drive organic growth** via referral chain rewards
- **Enable sales-driven redemptions** where commercial staff curate rewards from a catalog
- **Avoid app fragmentation** by integrating within existing `ls_shop` codebase

---

## Goals

1. **Automatic Point Award** on Sales Order submit (COD payment mode)
2. **Multi-level Affiliate Rewards** — traverse referral chain upward (A buys → B(L1), C(L2), D(L3))
3. **Configurable Reward Plans** — define earning rules, affiliate percentages, point expiration
4. **Reward Catalog** — products exchangeable for points, managed by sales
5. **Back-office Redemption** — sales persons create redemptions, system auto-generates Delivery Note at 0 MAD
6. **Portal Integration** — customers see balance, history, referral code, catalog (view-only)
7. **Referral Code System** — new customers can enter referrer code during signup
8. **Point Reversal** — on order cancellation or return
9. **Point Expiration** — per Reward Plan configuration

---

## Non-goals

- **Customer self-redemption** — redemptions are sales-person only
- **Cash conversion** — points cannot be exchanged for money
- **Non-COD payment modes** — points only for COD orders (initial scope)
- **External API integrations** — no third-party loyalty platforms
- **Mobile app** — web portal only

---

## Capabilities

### New Capabilities

- **`reward-plan`**: Configure earning rules, affiliate levels, expiration periods
- **`affiliate-chain`**: Traverse referral hierarchy for multi-level rewards
- **`point-ledger`**: Track all point transactions with full audit trail
- **`reward-catalog`**: Manage products exchangeable for points
- **`redemption`**: Sales-person initiated reward redemption with Delivery Note generation
- **`portal-points`**: Customer-facing balance, history, referral sharing

### Modified Capabilities

- **`customer-signup`**: Add optional referral code field
- **`sales-order`**: Hook for point award on COD submit + reversal on cancel

---

## Impact

| Area | Change |
|------|--------|
| **Database** | 7 new DocTypes, custom fields on Customer |
| **Hooks** | `on_submit`/`on_cancel` on Sales Order; `on_submit`/`on_cancel` on Reward Redemption; `before_insert` on Customer |
| **API** | 4 new whitelist endpoints for portal |
| **Templates** | Override `sign-up.html` and `my-account.html` |
| **Client Scripts** | Form scripts for Reward Redemption UX |
| **Fixtures** | Custom fields exported for Customer `referred_by`, `referral_code`, `reward_tier` |

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **All code in `ls_shop`** | Avoid circular deps, installation ordering issues, distribution not needed |
| **Points on Sales Order submit** | COD flow; invoice may come much later |
| **Chain traversal stops at 0% level** | Prevents rewarding distant relatives when intermediate tier disabled |
| **Circular reference protection** | `visited` set prevents infinite loops in malformed referral chains |
| **Level = inherited from referrer** | Creates tier-based incentive structure |
| **Sales Person = logged-in user** | Simple assignment for back-office redemptions |

