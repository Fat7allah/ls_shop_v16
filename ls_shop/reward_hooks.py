# Copyright (c) 2026, Ls Shop and contributors
# For license information, please see license.txt

import math
import frappe
from frappe.utils import today, getdate, add_days


# ============================================================================
# Customer Hooks
# ============================================================================

def generate_referral_code(doc, method):
    """Generate unique referral code and inherit tier from referrer"""
    if not doc.referral_code:
        doc.referral_code = "REF-" + frappe.generate_hash(length=8).upper()
    
    # Inherit tier from referrer if provided
    if doc.referred_by and not doc.reward_tier:
        referrer_tier = frappe.db.get_value("Customer", doc.referred_by, "reward_tier")
        doc.reward_tier = referrer_tier or "Bronze"
    elif not doc.reward_tier:
        doc.reward_tier = "Bronze"


# ============================================================================
# Sales Order Hooks
# ============================================================================

def on_submit_sales_order(doc, method):
    """Award points when COD Sales Order is submitted"""
    # Only process COD orders
    if doc.custom_ecommerce_payment_mode != "COD":
        return
    
    # Idempotence check
    if already_processed(doc.name, "Sales Order"):
        frappe.log_error(f"Reward points already processed for {doc.name}", "Reward Points")
        return
    
    # Find applicable reward plan
    plan = get_applicable_reward_plan(doc)
    if not plan:
        return
    
    # Calculate base points
    base_points = calculate_base_points(doc, plan)
    if base_points <= 0:
        return
    
    # Award points to customer and affiliates
    award_points(doc, plan, base_points)


def on_cancel_sales_order(doc, method):
    """Reverse points when Sales Order is cancelled"""
    if doc.custom_ecommerce_payment_mode != "COD":
        return
    
    # Find existing point entries for this order
    entries = frappe.get_all(
        "Customer Reward Points",
        filters={
            "reference_document_type": "Sales Order",
            "reference_name": doc.name,
            "transaction_type": ["in", ["Invoice Reward", "Affiliate Reward"]]
        },
        fields=["name", "customer", "points", "transaction_type", "level"]
    )
    
    if not entries:
        return
    
    # Reverse each entry
    for entry in entries:
        # Check if already reversed
        existing_reversal = frappe.db.exists(
            "Customer Reward Points",
            {
                "reference_document_type": "Sales Order",
                "reference_name": doc.name,
                "transaction_type": "Order Cancellation Reversal",
                "customer": entry.customer
            }
        )
        
        if existing_reversal:
            continue
        
        # Create reversal entry (negative of the original)
        create_reward_entry(
            customer=entry.customer,
            points=-entry.points,  # Reverse the original points
            transaction_type="Order Cancellation Reversal",
            reference_doctype="Sales Order",
            reference_name=doc.name,
            plan=None,
            level=entry.level,
            remarks=f"Reversal due to order cancellation: {doc.name}"
        )


# ============================================================================
# Reward Redemption Hooks
# ============================================================================

def before_submit_redemption(doc, method):
    """Validate sufficient balance before redemption"""
    balance = get_customer_balance(doc.customer)
    doc.current_balance = balance
    
    # Calculate total points
    total = 0
    for item in doc.redemption_items:
        item.total_points = (item.points_per_unit or 0) * (item.quantity or 0)
        total += item.total_points
    
    doc.total_points_used = total
    
    if total > balance:
        frappe.throw(
            f"Solde insuffisant. Le client dispose de {balance} points "
            f"mais cette rédemption nécessite {total} points."
        )


def on_submit_redemption(doc, method):
    """Debit points and create Delivery Note on redemption"""
    # Debit points
    create_reward_entry(
        customer=doc.customer,
        points=-doc.total_points_used,
        transaction_type="Redemption",
        reference_doctype="Reward Redemption",
        reference_name=doc.name,
        plan=None,
        level=0,
        remarks=f"Rédemption par {doc.sales_person}"
    )
    
    # Create Delivery Note (only if not already created)
    if not doc.delivery_note:
        dn = create_delivery_note_for_redemption(doc)
        frappe.db.set_value("Reward Redemption", doc.name, "delivery_note", dn.name)


def on_cancel_redemption(doc, method):
    """Re-credit points and cancel Delivery Note on redemption cancellation"""
    # Re-credit points
    create_reward_entry(
        customer=doc.customer,
        points=doc.total_points_used,
        transaction_type="Redemption Reversal",
        reference_doctype="Reward Redemption",
        reference_name=doc.name,
        plan=None,
        level=0,
        remarks=f"Annulation rédemption {doc.name}"
    )
    
    # Cancel Delivery Note
    if doc.delivery_note:
        dn = frappe.get_doc("Delivery Note", doc.delivery_note)
        if dn.docstatus == 1:
            dn.cancel()


# ============================================================================
# Helper Functions
# ============================================================================

def get_applicable_reward_plan(order):
    """Find the first active reward plan applicable to this order"""
    customer_group = frappe.db.get_value("Customer", order.customer, "customer_group")
    
    plans = frappe.get_all(
        "Reward Plan",
        filters={"status": "Active"},
        fields=["name", "reward_plan_type", "customer_group", "item_group",
                "minimum_invoice_amount", "points_per_amount", "levels", "expiration_days"],
        order_by="creation asc"
    )
    
    for plan in plans:
        # Check customer group match
        group_match = (
            not plan.customer_group or
            plan.customer_group == customer_group or
            plan.customer_group == "All"
        )
        
        if group_match:
            return frappe.get_doc("Reward Plan", plan.name)
    
    return None


def calculate_base_points(order, plan):
    """Calculate base points based on plan type"""
    if plan.reward_plan_type == "Based on Invoice Amount":
        if order.grand_total < plan.minimum_invoice_amount:
            return 0
        return math.floor(order.grand_total / plan.points_per_amount)
    
    elif plan.reward_plan_type == "Based on Item Reward Points":
        # Build map of item codes to reward points
        plan_items = {
            row.item: row.reward_points 
            for row in plan.item_reward_points
        }
        
        total = 0
        for item in order.items:
            if item.item_code in plan_items:
                total += plan_items[item.item_code] * item.qty
        
        return total
    
    return 0


def award_points(order, plan, base_points):
    """Award points to customer and affiliates"""
    # Calculate expiration date
    expiration_date = None
    if plan.expiration_days and plan.expiration_days > 0:
        expiration_date = add_days(today(), plan.expiration_days)
    
    # Award to direct customer (level 0)
    create_reward_entry(
        customer=order.customer,
        points=base_points,
        transaction_type="Invoice Reward",
        reference_doctype="Sales Order",
        reference_name=order.name,
        plan=plan.name,
        level=0,
        expiration_date=expiration_date,
        remarks=f"Commande {order.name}"
    )
    
    # Traverse affiliate chain
    current_customer = order.customer
    affiliate_levels = {
        row.level: row.percentage 
        for row in plan.affiliate_level_table
    }
    visited = {current_customer}  # Prevent circular loops
    
    for level in range(1, plan.levels + 1):
        referrer = frappe.db.get_value("Customer", current_customer, "referred_by")
        
        if not referrer or referrer in visited:
            break
        
        visited.add(referrer)
        percentage = affiliate_levels.get(level, 0)
        
        # Stop traversal if percentage is 0
        if percentage == 0:
            break
        
        if percentage > 0:
            affiliate_points = math.floor(base_points * (percentage / 100))
            if affiliate_points > 0:
                create_reward_entry(
                    customer=referrer,
                    points=affiliate_points,
                    transaction_type="Affiliate Reward",
                    reference_doctype="Sales Order",
                    reference_name=order.name,
                    plan=plan.name,
                    level=level,
                    expiration_date=expiration_date,
                    remarks=f"Parrainage niveau {level} - commande {order.name}"
                )
        
        current_customer = referrer


def create_reward_entry(customer, points, transaction_type, reference_doctype,
                       reference_name, plan, level, remarks=None, expiration_date=None):
    """Create a ledger entry for reward points"""
    doc = frappe.new_doc("Customer Reward Points")
    doc.customer = customer
    doc.points = points
    doc.transaction_type = transaction_type
    doc.reference_document_type = reference_doctype
    doc.reference_name = reference_name
    doc.reward_plan = plan
    doc.level = level
    doc.date = today()
    doc.remarks = remarks
    doc.expiration_date = expiration_date
    doc.insert(ignore_permissions=True)
    
    return doc


def already_processed(doc_name, doc_type):
    """Check if points were already awarded for this document"""
    return frappe.db.exists(
        "Customer Reward Points",
        {
            "reference_document_type": doc_type,
            "reference_document_name": doc_name,
            "transaction_type": ["in", ["Invoice Reward", "Affiliate Reward"]]
        }
    )


def get_customer_balance(customer):
    """Calculate available (non-expired) point balance"""
    result = frappe.db.sql(
        """
        SELECT COALESCE(SUM(points), 0) as balance
        FROM `tabCustomer Reward Points`
        WHERE customer = %s
        AND (expiration_date IS NULL OR expiration_date >= %s)
        """,
        (customer, today()),
        as_dict=True
    )
    
    return int(result[0].balance) if result else 0


def create_delivery_note_for_redemption(redemption):
    """Create a Delivery Note at 0 MAD for reward redemption"""
    from frappe.utils import get_defaults
    
    company = get_defaults().get("company")
    warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
    
    if not warehouse:
        frappe.throw("Default warehouse not configured in Stock Settings")
    
    dn = frappe.new_doc("Delivery Note")
    dn.customer = redemption.customer
    dn.posting_date = redemption.redemption_date
    dn.company = company
    dn.custom_reward_redemption = redemption.name
    
    for item in redemption.redemption_items:
        dn.append("items", {
            "item_code": item.item,
            "qty": item.quantity,
            "rate": 0,
            "amount": 0,
            "warehouse": warehouse
        })
    
    dn.insert(ignore_permissions=True)
    dn.submit()
    
    return dn
