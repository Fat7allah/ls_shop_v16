# LS Shop Demo Data Script

This script automatically populates your LS Shop installation with demo data for testing the complete e-commerce workflow.

## What Gets Created

### ERPNext Prerequisites
- **Item Attributes**
  - Color (Red, Blue, Black, White, Green, Navy, Gray)
  - Size (XS, S, M, L, XL, XXL)

- **Brands**
  - Adidas
  - Nike
  - Puma
  - Lifestyle Store

- **Price Lists**
  - Standard Selling (USD)
  - Sale Price List (USD)

- **Shipping Rule**
  - Standard Shipping
  - $10 shipping for orders under $50
  - Free shipping for orders $50 and above

### LS Shop Configuration

- **Lifestyle Settings** - Fully configured with:
  - Default price lists
  - Ecommerce warehouse
  - Shipping rules
  - Return period (30 days)
  - COD settings ($5 fee for orders under $100)
  - Email templates
  - Return reasons

### Demo Products

The script creates **3 complete product lines** with full variant support:

#### 1. Classic Cotton T-Shirt
- **Brand**: Lifestyle Store
- **Category**: Men
- **Colors**: Black, White, Navy, Gray (4 colors)
- **Sizes**: S, M, L, XL, XXL (5 sizes)
- **Price**: $29.99 (Regular) / $24.99 (Sale)
- **Total Variants**: 20 SKUs

#### 2. Slim Fit Denim Jeans
- **Brand**: Lifestyle Store
- **Category**: Men
- **Colors**: Blue, Black (2 colors)
- **Sizes**: S, M, L, XL (4 sizes)
- **Price**: $79.99 (Regular) / $69.99 (Sale)
- **Total Variants**: 8 SKUs

#### 3. Running Sneakers
- **Brand**: Adidas
- **Category**: Men
- **Colors**: Black, White, Blue (3 colors)
- **Sizes**: S, M, L, XL (4 sizes)
- **Price**: $119.99 (Regular) / $99.99 (Sale)
- **Total Variants**: 12 SKUs

**Total Demo SKUs**: ~40 product variants

### Additional Features

- ✅ **Style Attribute Configurators** (SAC) - One per product template
- ✅ **Style Attribute Variants** (SAV) - One per color variant with demo images
- ✅ **Color Size Items** - Links all size variants to their colors
- ✅ **Proper Routing** - All products use `/en/products/` format
- ✅ **Demo Images** - Placeholder images with product names and colors
- ✅ **Stock Quantities** - Random stock (50-200 units per variant)
- ✅ **Dual Pricing** - Regular and sale prices

---

## Installation

### Prerequisites

1. **LS Shop must be installed first**:
   ```bash
   bench --site your-site-name install-app ls_shop
   ```

2. **ERPNext Company and Warehouse** should exist
   - At least one Company created
   - At least one non-group Warehouse available

### Running the Script

```bash
bench --site your-site-name execute ls_shop.ls_shop.install_demo_data.install_demo_data
```

### Expected Output

```
============================================================
Installing LS Shop Demo Data
============================================================

Step 1: Creating Prerequisites...
  - Creating Item Attributes...
    ✓ Color attribute created
    ✓ Size attribute created
  - Creating Brands...
    ✓ Brand 'Adidas' created
    ✓ Brand 'Nike' created
    ✓ Brand 'Puma' created
    ✓ Brand 'Lifestyle Store' created
  - Creating Price Lists...
    ✓ Price List 'Standard Selling' created
    ✓ Price List 'Sale Price List' created
  - Creating Shipping Rule...
    ✓ Shipping Rule 'Standard Shipping' created

Step 2: Configuring Lifestyle Settings...
  - Configuring Lifestyle Settings...
    ✓ Lifestyle Settings configured

Step 3: Creating Demo Products...

  Creating product: Classic Cotton T-Shirt
    ✓ Template 'TSHIRT-CLASSIC' created
    ✓ Configurator created for 'TSHIRT-CLASSIC'
    ✓ Style variant 'Black' created
    ✓ Style variant 'White' created
    ✓ Style variant 'Navy' created
    ✓ Style variant 'Gray' created
    ✓ All variants created for TSHIRT-CLASSIC

  Creating product: Slim Fit Denim Jeans
    ✓ Template 'JEANS-SLIM' created
    ✓ Configurator created for 'JEANS-SLIM'
    ✓ Style variant 'Blue' created
    ✓ Style variant 'Black' created
    ✓ All variants created for JEANS-SLIM

  Creating product: Running Sneakers
    ✓ Template 'SNEAKER-RUN' created
    ✓ Configurator created for 'SNEAKER-RUN'
    ✓ Style variant 'Black' created
    ✓ Style variant 'White' created
    ✓ Style variant 'Blue' created
    ✓ All variants created for SNEAKER-RUN

Step 4: Fixing Product Routes...
  - Updating product routes...
    ✓ Updated 40 product routes

============================================================
✅ Demo Data Installation Complete!
============================================================

You can now access the shop at:
  English: https://your-site.com/en/products
  Arabic:  https://your-site.com/ar/products

Demo products created:
  - Classic T-Shirt (Multiple colors & sizes)
  - Slim Fit Jeans (Multiple colors & sizes)
  - Running Sneakers (Multiple colors & sizes)
```

---

## What You Can Test

After running the demo data script, you can test:

### 1. Product Browsing
- Visit `/en/products` to see all products
- Filter by brand, color, size
- Search for products
- View product details

### 2. Product Variants
- Select different colors to see images
- Choose sizes and see stock availability
- View different price points (regular vs sale)

### 3. Shopping Cart
- Add products to cart
- Update quantities
- Remove items
- See price calculations with shipping

### 4. Checkout Process
- Guest checkout
- User registration and login
- Address management
- Payment method selection (COD configured)

### 5. Backend Management
- View **Style Attribute Configurators** (SAC)
- Manage **Style Attribute Variants** (SAV)
- Check **Website Items** with proper routes
- Review **Item Prices** for both price lists

---

## Customizing Demo Data

### Adding More Products

Edit the `products` list in [`install_demo_data.py`](install_demo_data.py:56):

```python
products = [
    {
        "code": "YOUR-PRODUCT-CODE",
        "name": "Your Product Name",
        "item_group": "Men",  # or "Women", "Kids"
        "brand": "Your Brand",
        "description": "Product description",
        "colors": ["Red", "Blue", "Black"],
        "sizes": ["S", "M", "L", "XL"],
        "base_price": 49.99,
        "sale_price": 39.99
    },
    # ... add more products
]
```

### Using Real Images

Replace placeholder image URLs in the `create_style_variant()` function:

```python
"images": [
    {
        "image": "https://your-cdn.com/product-images/tshirt-red.jpg",
    }
]
```

### Changing Pricing

Modify prices in the product definitions or adjust price list percentages.

---

## Cleaning Up Demo Data

To remove demo data:

```python
# In bench console
bench --site your-site-name console

# Then run:
import frappe

# Delete demo items
demo_codes = ["TSHIRT-CLASSIC", "JEANS-SLIM", "SNEAKER-RUN"]
for code in demo_codes:
    # Delete variants first
    variants = frappe.get_all("Item", {"variant_of": code})
    for v in variants:
        frappe.delete_doc("Item", v.name, force=True)
    
    # Delete template
    if frappe.db.exists("Item", code):
        frappe.delete_doc("Item", code, force=True)

# Delete configurators
configurators = frappe.get_all("Style Attribute Configurator")
for c in configurators:
    frappe.delete_doc("Style Attribute Configurator", c.name, force=True)

frappe.db.commit()
```

---

## Troubleshooting

### Script Fails with "Company not found"

Create a company first:
```bash
bench --site your-site-name console
```
Then:
```python
company = frappe.get_doc({
    "doctype": "Company",
    "company_name": "Demo Company",
    "abbr": "DC",
    "country": "United States",
    "default_currency": "USD"
})
company.insert(ignore_permissions=True)
frappe.db.commit()
```

### Script Fails with "Warehouse not found"

Create a warehouse first or the script will use default "Stores - LSE".

### Products Not Showing on Website

1. Check that Item Groups are published:
   - Go to **Stock → Item Group → Men/Women/Kids**
   - Ensure "Display on Website" is checked
   - Ensure "Show in Website" is checked

2. Clear cache:
```bash
bench --site your-site-name clear-cache
bench --site your-site-name clear-website-cache
```

### Routes Still Using Old Format

Run the route fix separately:
```bash
bench --site your-site-name console
```
Then:
```python
from ls_shop.install_demo_data import fix_product_routes
fix_product_routes()
frappe.db.commit()
```

---

## Next Steps After Demo Data

1. **Explore the Frontend**
   - Browse products at `/en/products`
   - Test filtering by brand, color, size
   - Try the search functionality

2. **Test Complete Purchase Flow**
   - Add items to cart
   - Proceed to checkout
   - Complete a test order with COD

3. **Customize Products**
   - Edit product descriptions
   - Upload real product images
   - Adjust pricing

4. **Configure Payment Gateways**
   - Set up Telr for online payments
   - Configure Tabby for BNPL
   - Test payment flows

5. **Add Real Products**
   - Follow the main setup guide to add your actual products
   - Use the demo data as a reference for structure

---

## Script Details

### Functions Overview

- `install_demo_data()` - Main orchestrator function
- `create_item_attributes()` - Creates Color and Size attributes
- `create_brands()` - Creates demo brands
- `create_price_lists()` - Creates selling price lists
- `create_shipping_rule()` - Creates shipping rule with conditions
- `configure_lifestyle_settings()` - Configures all LS Shop settings
- `create_demo_products()` - Creates all demo products
- `create_product_with_variants()` - Creates a single product with variants
- `create_item_template()` - Creates item template (parent)
- `create_configurator()` - Creates Style Attribute Configurator
- `create_style_variant()` - Creates Style Attribute Variant for each color
- `create_item_variants()` - Creates all actual item variants (SKUs)
- `fix_product_routes()` - Updates routes to LS Shop format

### Database Transactions

The script uses:
- `frappe.db.commit()` - On successful completion
- `frappe.db.rollback()` - On any error
- `ignore_permissions=True` - For demo data creation

---

## Support

If you encounter issues with the demo data script:

1. Check the Error Log in Frappe Desk
2. Review the console output for specific errors
3. Ensure all prerequisites are met
4. Try running individual functions in bench console for debugging

---

**Last Updated**: 2025-10-03