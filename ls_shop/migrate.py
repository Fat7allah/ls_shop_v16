import frappe


def after_install():
	create_payment_modes()
	try:
		create_default_email_templates()
	except Exception as e:
		import traceback

		error_msg = f"Error creating default email templates: {e!s}"
		frappe.log_error(traceback.format_exc(), "Lifestyle Shop Installation - Email Templates")
		frappe.errprint(error_msg)
		frappe.errprint(traceback.format_exc())

	register_optional_doctype_links()


def after_migrate():
	register_optional_doctype_links()


def register_optional_doctype_links():
	"""Add Customize Form connections for optional integrations whose doctypes are
	provided by tabby_frappe.
	"""
	add_sales_order_link_if_doctype_exists("Tabby Payment Request", "ref_docname")


def add_sales_order_link_if_doctype_exists(link_doctype: str, link_fieldname: str):
	if not frappe.db.exists("DocType", link_doctype):
		return

	customize_form = frappe.get_doc({"doctype": "Customize Form", "doc_type": "Sales Order"})
	customize_form.run_method("fetch_to_customize")
	if any(row.link_doctype == link_doctype for row in (customize_form.get("links") or [])):
		return

	customize_form.append(
		"links",
		{
			"link_doctype": link_doctype,
			"link_fieldname": link_fieldname,
		},
	)
	try:
		customize_form.save()
	except Exception:
		import traceback

		frappe.log_error(traceback.format_exc(), f"ls_shop: optional link for {link_doctype}")


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
			"reference_doctype": "Sales Order",
		},
		{
			"name": "Item In Stock",
			"subject": "Item Back in Stock - {{ item.item_name }}",
			"response": """Dear Customer,

Great news! The item "{{ item.item_name }}" is now back in stock.

You can purchase it now at: {{ item_url }}

Best regards,
{{ company }}""",
			"reference_doctype": "Item",
		},
		{
			"name": "Order Cancellation",
			"subject": "Order Cancellation Confirmation - {{ doc.name }}",
			"response": """Dear {{ doc.customer_name }},

Your order {{ doc.name }} has been cancelled as requested.

If you have any questions, please contact our customer service.

Best regards,
{{ company }}""",
			"reference_doctype": "Sales Order",
		},
	]

	for template_data in email_templates:
		if not frappe.db.exists("Email Template", template_data["name"]):
			template = frappe.get_doc({"doctype": "Email Template", **template_data})
			template.insert(ignore_permissions=True)
			frappe.errprint(f"Created Email Template: {template_data['name']}")
		else:
			frappe.errprint(f"Email Template '{template_data['name']}' already exists")
