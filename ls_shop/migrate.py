import frappe


def after_install():
	create_payment_modes()
	try:
		create_default_email_templates()
		create_ecommerce_group()
		create_ecommerce_categories()
		create_default_footer_sections()
	except Exception as e:
		import traceback
		error_msg = f"Error creating Ecommerce groups/categories: {str(e)}"
		frappe.log_error(traceback.format_exc(), "Lifestyle Shop Installation - Ecommerce Setup")
		frappe.errprint(error_msg)
		frappe.errprint(traceback.format_exc())


def create_payment_modes():
	modes = {"Telr"}

	for mode in modes:
		frappe.get_doc(
			{
				"doctype": "Mode of Payment",
				"mode_of_payment": mode,
				"enabled": True,
				"type": "Bank",
			}
		).insert(ignore_if_duplicate=True)


# Create ecommerce item group


def create_ecommerce_group():
	"""Create Ecommerce Website parent and car parts category item groups"""
	parent = "Ecommerce Website"
	
	# Car parts categories (matching Ecommerce Category doctype)
	parent_categories = {
		"Engine Parts": "Engine Parts",
		"Brake System": "Brake System",
		"Interior Accessories": "Interior Accessories"
	}
	
	# Find or create root item group
	root_item_group = get_root_item_group()
	
	# Create parent group
	frappe.get_doc(
		{
			"doctype": "Item Group",
			"item_group_name": parent,
			"is_group": True,
			"parent_item_group": root_item_group,
			"custom_displayname": parent,
			"custom_item_group_display_name": parent,
		}
	).insert(ignore_if_duplicate=True)
	
	# Create car parts category item groups
	for category_name, display_name in parent_categories.items():
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": category_name,
				"is_group": True,
				"parent_item_group": parent,
				"custom_displayname": display_name,
				"custom_item_group_display_name": display_name,
			}
		).insert(ignore_if_duplicate=True)


def get_root_item_group():
	"""Find or create the root item group"""
	# Try to find existing root item group (parent_item_group is null)
	root_groups = frappe.get_all(
		"Item Group",
		filters={"parent_item_group": ["in", ["", None]]},
		fields=["name"],
		limit=1
	)
	
	if root_groups:
		return root_groups[0].name
	
	# If no root exists, create "All Item Groups"
	root_name = "All Item Groups"
	if not frappe.db.exists("Item Group", root_name):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": root_name,
				"is_group": True,
				"parent_item_group": "",
				"custom_displayname": root_name,
				"custom_item_group_display_name": root_name,
			}
		).insert(ignore_permissions=True)
	
	return root_name


def create_default_email_templates():
	"""Create default email templates required by Lifestyle Settings"""

	email_templates = [
		{
			"name": "Order Confirmation",
			"subject": "Order Confirmation - {{ doc.name }}",
			"response": """Dear {{ doc.customer_name }},

Thank you for your order! Your order has been confirmed.

Order Details:
Order ID: {{ doc.name }}
Date: {{ doc.transaction_date }}
Total: {{ doc.grand_total }}

You can track your order status at: {{ login_url }}

Best regards,
{{ company }}""",
			"doctype": "Sales Order"
		},
		{
			"name": "Item In Stock",
			"subject": "Item Back in Stock - {{ item.item_name }}",
			"response": """Dear Customer,

Great news! The item "{{ item.item_name }}" is now back in stock.

You can purchase it now at: {{ item_url }}

Best regards,
{{ company }}""",
			"doctype": "Item"
		},
		{
			"name": "Order Cancellation",
			"subject": "Order Cancellation Confirmation - {{ doc.name }}",
			"response": """Dear {{ doc.customer_name }},

Your order {{ doc.name }} has been cancelled as requested.

If you have any questions, please contact our customer service.

Best regards,
{{ company }}""",
			"doctype": "Sales Order"
		}
	]

	for template_data in email_templates:
		if not frappe.db.exists("Email Template", template_data["name"]):
			template = frappe.get_doc({
				"doctype": "Email Template",
				**template_data
			})
			template.insert(ignore_permissions=True)
			frappe.errprint(f"Created Email Template: {template_data['name']}")
		else:
			frappe.errprint(f"Email Template '{template_data['name']}' already exists")


def create_ecommerce_categories():
	"""Create default Ecommerce Categories (now database-driven instead of hardcoded)"""

	# Default categories - users can rename or modify these later
	# Using car parts theme as per requirements
	categories = [
		{
			"category_name": "Engine Parts",
			"display_name": "Engine Parts",
			"route_slug": "engine-parts",
			"item_group": "Engine Parts",  # Links to Item Group created above
			"enabled": 1,
			"display_order": 1
		},
		{
			"category_name": "Brake System",
			"display_name": "Brake System",
			"route_slug": "brake-system",
			"item_group": "Brake System",  # Links to Item Group created above
			"enabled": 1,
			"display_order": 2
		},
		{
			"category_name": "Interior Accessories",
			"display_name": "Interior Accessories",
			"route_slug": "interior-accessories",
			"item_group": "Interior Accessories",  # Links to Item Group created above
			"enabled": 1,
			"display_order": 3
		}
	]

	for cat_data in categories:
		if not frappe.db.exists("Ecommerce Category", cat_data["category_name"]):
			cat = frappe.get_doc({
				"doctype": "Ecommerce Category",
				**cat_data
			})
			cat.insert(ignore_permissions=True)
			frappe.errprint(f"Created Ecommerce Category: {cat_data['category_name']}")
		else:
			frappe.errprint(f"Ecommerce Category '{cat_data['category_name']}' already exists")


def create_default_footer_sections():
	"""Create default footer sections in Lifestyle Settings"""

	if not frappe.db.exists("Lifestyle Settings", "Lifestyle Settings"):
		frappe.errprint("Lifestyle Settings not found, skipping footer sections")
		return

	settings = frappe.get_doc("Lifestyle Settings", "Lifestyle Settings")

	# Set default email templates if not already set (required fields)
	if not settings.order_confirmation_email_template:
		settings.order_confirmation_email_template = "Order Confirmation"

	if not settings.item_in_stock_email_template:
		settings.item_in_stock_email_template = "Item In Stock"

	if not settings.order_cancellation_email_template:
		settings.order_cancellation_email_template = "Order Cancellation"

	# Only create if no footer sections exist
	if settings.footer_sections:
		frappe.errprint("Footer sections already exist, skipping")
		return
	
	# Default footer sections with common e-commerce links
	default_sections = [
		{
			"section_title": "My Account",
			"section_order": 1,
			"enabled": 1,
			"footer_links": [
				{"link_label": "My Account", "link_url": "/account/dashboard", "link_order": 1, "enabled": 1},
				{"link_label": "Orders History", "link_url": "/account/orders", "link_order": 2, "enabled": 1},
				{"link_label": "Wishlist", "link_url": "/account/wishlist", "link_order": 3, "enabled": 1},
				{"link_label": "Track Order", "link_url": "#", "link_order": 4, "enabled": 1},
			]
		},
		{
			"section_title": "Policies",
			"section_order": 2,
			"enabled": 1,
			"footer_links": [
				{"link_label": "Privacy Policy", "link_url": "#", "link_order": 1, "enabled": 1},
				{"link_label": "Terms and Conditions", "link_url": "#", "link_order": 2, "enabled": 1},
				{"link_label": "Shipping Policy", "link_url": "#", "link_order": 3, "enabled": 1},
				{"link_label": "Returns Policy", "link_url": "#", "link_order": 4, "enabled": 1},
				{"link_label": "Payment Policy", "link_url": "#", "link_order": 5, "enabled": 1},
			]
		},
		{
			"section_title": "Customer Service",
			"section_order": 3,
			"enabled": 1,
			"footer_links": [
				{"link_label": "FAQ", "link_url": "#", "link_order": 1, "enabled": 1},
				{"link_label": "Contact Us", "link_url": "#", "link_order": 2, "enabled": 1},
				{"link_label": "Sizing Charts", "link_url": "#", "link_order": 3, "enabled": 1},
				{"link_label": "International Shipping", "link_url": "#", "link_order": 4, "enabled": 1},
			]
		}
	]
	
	for section_data in default_sections:
		settings.append("footer_sections", section_data)
	
	settings.save(ignore_permissions=True)
	frappe.errprint("✅ Default footer sections created")
