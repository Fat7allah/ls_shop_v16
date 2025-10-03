import frappe


def after_install():
	create_payment_modes()
	try:
		create_ecommerce_group()
	except Exception as e:
		import traceback
		error_msg = f"Error creating Ecommerce groups: {str(e)}"
		frappe.log_error(traceback.format_exc(), "Lifestyle Shop Installation - Ecommerce Groups")
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
	parent = "Ecommerce Website"
	parent_categories = {"Men", "Women", "Kids"}
	
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
	
	for category in parent_categories:
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": category,
				"is_group": True,
				"parent_item_group": parent,
				"custom_displayname": category,
				"custom_item_group_display_name": category,
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
