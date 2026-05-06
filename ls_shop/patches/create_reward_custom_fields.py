"""Create custom fields for Reward Points System"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """Create custom fields on Customer and Delivery Note"""
    
    # Custom fields for Customer
    customer_fields = [
        {
            "fieldname": "referred_by",
            "label": "Referred By",
            "fieldtype": "Link",
            "options": "Customer",
            "insert_after": "customer_group",
            "description": "Customer who referred this customer",
            "print_hide": 1,
        },
        {
            "fieldname": "referral_code",
            "label": "Referral Code",
            "fieldtype": "Data",
            "insert_after": "referred_by",
            "description": "Unique referral code for this customer",
            "unique": 1,
            "read_only": 1,
            "print_hide": 1,
        },
        {
            "fieldname": "reward_tier",
            "label": "Reward Tier",
            "fieldtype": "Select",
            "options": "\nBronze\nSilver\nGold",
            "insert_after": "referral_code",
            "description": "Customer tier for reward catalog access",
            "default": "Bronze",
            "print_hide": 1,
        },
    ]
    
    # Custom fields for Delivery Note
    delivery_note_fields = [
        {
            "fieldname": "reward_redemption",
            "label": "Reward Redemption",
            "fieldtype": "Link",
            "options": "Reward Redemption",
            "insert_after": "customer",
            "description": "Reward Redemption that created this Delivery Note",
            "read_only": 1,
            "print_hide": 1,
        },
    ]
    
    # Create Customer fields
    for field in customer_fields:
        try:
            create_custom_field("Customer", field)
            print(f"Created custom field: Customer.{field['fieldname']}")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                print(f"Field already exists: Customer.{field['fieldname']}")
            else:
                print(f"Error creating Customer.{field['fieldname']}: {e}")
    
    # Create Delivery Note fields
    for field in delivery_note_fields:
        try:
            create_custom_field("Delivery Note", field)
            print(f"Created custom field: Delivery Note.{field['fieldname']}")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                print(f"Field already exists: Delivery Note.{field['fieldname']}")
            else:
                print(f"Error creating Delivery Note.{field['fieldname']}: {e}")
    
    frappe.db.commit()
    print("Custom fields creation complete")
