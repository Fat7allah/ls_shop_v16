# Copyright (c) 2026, Ls Shop and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, getdate


@frappe.whitelist()
def get_customer_balance(customer):
    """Get current available point balance for a customer"""
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
    
    balance = int(result[0].balance) if result else 0
    
    return {
        "balance": balance,
        "customer": customer
    }


@frappe.whitelist()
def get_active_catalog_items():
    """Get all active reward catalog items"""
    items = frappe.get_all(
        "Reward Catalog Item",
        filters={
            "is_active": 1,
            "valid_from": ["<=", today()],
            "valid_to": ["in", ["", None, [">=", today()]]]
        },
        fields=[
            "name", "item", "item_name", "item_image",
            "points_required", "description", "min_customer_level"
        ]
    )
    
    return items


@frappe.whitelist()
def get_customer_reward_summary():
    """Get complete reward summary for portal display"""
    # Get customer from session user
    customer = frappe.db.get_value(
        "Portal User",
        {"user": frappe.session.user},
        "parent"
    )
    
    if not customer:
        # Try finding customer through Contact
        contact = frappe.db.get_value("Contact", {"email_id": frappe.session.user}, "name")
        if contact:
            link = frappe.db.get_value(
                "Dynamic Link",
                {"parenttype": "Contact", "parent": contact, "link_doctype": "Customer"},
                "link_name"
            )
            customer = link
    
    if not customer:
        return {
            "balance": 0,
            "history": [],
            "referral_code": "",
            "catalog": [],
            "redemptions": [],
            "referral_count": 0
        }
    
    # Get balance
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
    balance = int(result[0].balance) if result else 0
    
    # Get transaction history
    history = frappe.get_all(
        "Customer Reward Points",
        filters={"customer": customer},
        fields=[
            "points", "transaction_type", "date",
            "reference_document_name", "remarks", "level"
        ],
        order_by="date desc, creation desc",
        limit=20
    )
    
    # Get active catalog with affordability indicator
    customer_tier = frappe.db.get_value("Customer", customer, "reward_tier")
    
    catalog_items = frappe.get_all(
        "Reward Catalog Item",
        filters={
            "is_active": 1,
            "valid_from": ["<=", today()],
            "valid_to": ["in", ["", None, [">=", today()]]]
        },
        fields=[
            "name", "item", "item_name", "item_image",
            "points_required", "description", "min_customer_level"
        ]
    )
    
    for item in catalog_items:
        # Check affordability
        item["affordable"] = balance >= item["points_required"]
        
        # Check tier access
        tier_levels = {"Bronze": 1, "Silver": 2, "Gold": 3}
        customer_level = tier_levels.get(customer_tier, 0)
        required_level = tier_levels.get(item["min_customer_level"], 0) if item["min_customer_level"] else 0
        item["tier_accessible"] = customer_level >= required_level
    
    # Get redemption history
    redemptions = frappe.get_all(
        "Reward Redemption",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "redemption_date", "total_points_used", "delivery_note"],
        order_by="redemption_date desc",
        limit=10
    )
    
    # Get referral info
    referral_code = frappe.db.get_value("Customer", customer, "referral_code")
    referral_count = frappe.db.count("Customer", {"referred_by": customer})
    
    return {
        "balance": balance,
        "history": history,
        "referral_code": referral_code,
        "catalog": catalog_items,
        "redemptions": redemptions,
        "referral_count": referral_count,
        "customer_tier": customer_tier
    }


@frappe.whitelist(allow_guest=True)
def validate_referral_code(code):
    """Validate a referral code and return referrer info"""
    if not code:
        return {"valid": False, "error": "No code provided"}
    
    referrer = frappe.db.get_value(
        "Customer",
        {"referral_code": code},
        ["name", "customer_name", "reward_tier"],
        as_dict=True
    )
    
    if not referrer:
        return {"valid": False, "error": "Invalid referral code"}
    
    return {
        "valid": True,
        "referrer": referrer.name,
        "referrer_name": referrer.customer_name,
        "referrer_tier": referrer.reward_tier
    }


@frappe.whitelist()
def set_referral_on_signup(customer_name, referral_code):
    """Set referred_by field when customer is created with referral code"""
    if not referral_code or not customer_name:
        return {"success": False}
    
    referrer = frappe.db.get_value(
        "Customer",
        {"referral_code": referral_code},
        "name"
    )
    
    if not referrer:
        frappe.log_error(
            f"Invalid referral code during signup: {referral_code}",
            "Referral Code"
        )
        return {"success": False, "error": "Invalid referral code"}
    
    try:
        customer = frappe.get_doc("Customer", customer_name)
        customer.referred_by = referrer
        
        # Inherit tier
        referrer_tier = frappe.db.get_value("Customer", referrer, "reward_tier")
        customer.reward_tier = referrer_tier or "Bronze"
        
        customer.save(ignore_permissions=True)
        return {"success": True, "referrer": referrer}
    except Exception as e:
        frappe.log_error(f"Error setting referral: {str(e)}", "Referral Code")
        return {"success": False, "error": str(e)}
