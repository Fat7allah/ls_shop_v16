# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr


class EcommerceCategory(Document):
	def validate(self):
		"""Validate before saving"""
		self.validate_route_slug()
		self.set_defaults()
	
	def validate_route_slug(self):
		"""Ensure route slug is unique and properly formatted"""
		if not self.route_slug:
			# Auto-generate from category_name
			self.route_slug = frappe.scrub(self.category_name)
		else:
			# Clean up the slug
			self.route_slug = frappe.scrub(self.route_slug)
		
		# Check for duplicates
		if self.route_slug:
			duplicate = frappe.db.get_value(
				"Ecommerce Category",
				{"route_slug": self.route_slug, "name": ["!=", self.name]},
				"name"
			)
			if duplicate:
				frappe.throw(f"Route slug '{self.route_slug}' is already used by {duplicate}")
	
	def set_defaults(self):
		"""Set default values"""
		if not self.display_name:
			self.display_name = self.category_name


@frappe.whitelist()
def get_active_categories():
	"""Get all active categories ordered by display_order"""
	return frappe.get_all(
		"Ecommerce Category",
		filters={"enabled": 1},
		fields=["name", "category_name", "display_name", "route_slug", "item_group", "icon", "image", "display_order"],
		order_by="display_order asc, category_name asc"
	)


@frappe.whitelist()
def get_category_by_slug(slug):
	"""Get category details by route slug"""
	return frappe.get_all(
		"Ecommerce Category",
		filters={"route_slug": slug, "enabled": 1},
		fields=["name", "category_name", "display_name", "route_slug", "item_group", "icon", "image"],
		limit=1
	)