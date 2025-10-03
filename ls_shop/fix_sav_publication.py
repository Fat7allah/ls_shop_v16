"""
Fix Style Attribute Variant publication
This script publishes all Style Attribute Variants that have Color Size Items
"""

import frappe


def fix_sav_publication():
	"""Publish all Style Attribute Variants"""
	
	print("Fixing Style Attribute Variant publication...")
	
	# Get all SAVs
	savs = frappe.get_all(
		"Style Attribute Variant",
		fields=["name", "display_name", "is_published"]
	)
	
	print(f"Found {len(savs)} Style Attribute Variants")
	
	published_count = 0
	
	for sav in savs:
		# Check if it has any Color Size Items
		has_sizes = frappe.db.exists("Color Size Item", {"parent": sav.name})
		
		if has_sizes and not sav.is_published:
			# Publish it
			frappe.db.set_value("Style Attribute Variant", sav.name, "is_published", 1)
			published_count += 1
			print(f"  ✓ Published: {sav.display_name}")
	
	frappe.db.commit()
	frappe.clear_cache()
	
	print(f"\n✅ Published {published_count} Style Attribute Variants")
	print(f"Total published SAVs: {frappe.db.count('Style Attribute Variant', {'is_published': 1})}")


if __name__ == "__main__":
	fix_sav_publication()