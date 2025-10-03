"""
Debug script to check why products aren't showing on website
"""

import frappe


def debug_product_display():
	"""Debug why products aren't showing"""
	
	print("\n" + "="*60)
	print("Debugging Product Display")
	print("="*60 + "\n")
	
	# Check Style Attribute Variants
	savs = frappe.get_all(
		"Style Attribute Variant",
		filters={"is_published": 1},
		fields=["name", "display_name", "is_published", "item_group"]
	)
	print(f"1. Style Attribute Variants (published): {len(savs)}")
	for sav in savs[:5]:
		print(f"   - {sav.name}: {sav.display_name} (Group: {sav.item_group})")
	
	# Check Color Size Items
	csis = frappe.get_all(
		"Color Size Item",
		fields=["name", "parent", "size", "item_code"]
	)
	print(f"\n2. Color Size Items: {len(csis)}")
	for csi in csis[:5]:
		print(f"   - Parent: {csi.parent}, Size: {csi.size}, Item: {csi.item_code}")
	
	# Check Item Prices
	prices = frappe.get_all(
		"Item Price",
		filters={"price_list": "Sale Price List"},
		fields=["item_code", "price_list_rate"]
	)
	print(f"\n3. Item Prices (Sale Price List): {len(prices)}")
	for price in prices[:5]:
		print(f"   - {price.item_code}: ${price.price_list_rate}")
	
	# Run the actual product query
	from ls_shop.utils import get_product_base_query, get_product_list
	
	print("\n4. Running Product Query...")
	try:
		products = get_product_list(filters={}, page=1, page_length=10)
		print(f"   Products returned: {len(products)}")
		for p in products[:3]:
			print(f"   - {p.get('display_name')}: ${p.get('sale_price')}")
	except Exception as e:
		print(f"   ❌ Error: {str(e)}")
		import traceback
		traceback.print_exc()
	
	# Check query components
	print("\n5. Checking Query Components...")
	lifestyle_settings = frappe.get_doc("Lifestyle Settings")
	print(f"   Default Price List: {lifestyle_settings.default_price_list}")
	print(f"   Sale Price List: {lifestyle_settings.sale_price_list}")
	
	# Check if SAVs have sizes populated
	print("\n6. Checking SAV Size Mappings...")
	savs_with_sizes = frappe.db.sql("""
		SELECT sav.name, sav.display_name, COUNT(csi.name) as size_count
		FROM `tabStyle Attribute Variant` sav
		LEFT JOIN `tabColor Size Item` csi ON csi.parent = sav.name
		WHERE sav.is_published = 1
		GROUP BY sav.name
		LIMIT 5
	""", as_dict=True)
	
	for sav in savs_with_sizes:
		print(f"   - {sav.name}: {sav.size_count} sizes")
	
	print("\n" + "="*60)


if __name__ == "__main__":
	debug_product_display()