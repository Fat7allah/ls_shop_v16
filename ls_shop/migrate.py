import frappe


def after_install():
	create_payment_modes()
	try:
		create_ecommerce_group()
		create_ecommerce_categories()
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
