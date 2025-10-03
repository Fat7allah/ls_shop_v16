# Ecommerce Category Implementation

## Overview

This implementation makes the category system dynamic and database-driven instead of hardcoded. Categories are now managed through the "Ecommerce Category" doctype, allowing administrators to easily customize categories without code changes.

## Changes Made

### 1. New Doctype: Ecommerce Category

**Location:** `ls_shop/lifestyle_shop_ecommerce/doctype/ecommerce_category/`

**Fields:**
- `category_name` - Unique identifier for the category
- `display_name` - Display name shown to users
- `route_slug` - URL-friendly slug for routing
- `enabled` - Toggle to enable/disable categories
- `display_order` - Sort order for display
- `item_group` - Optional link to existing Item Group for filtering
- `icon` - Optional icon name or CSS class
- `image` - Optional category image

**Features:**
- Auto-generates route slug from category name if not provided
- Validates unique route slugs
- Sortable by display_order
- Full CRUD permissions for System Manager

### 2. Updated Files

#### migrate.py
- Added `create_ecommerce_categories()` function
- Creates 3 default categories on installation:
  - Engine Parts (maps to Men item group)
  - Brake System (maps to Women item group)
  - Interior Accessories (maps to Kids item group)
- Categories are linked to existing item groups for backward compatibility

#### www/products/list.py
- Modified `get_product_filters()` to query categories from Ecommerce Category doctype
- Dynamically loads categories based on enabled status
- Falls back to item group hierarchy for subcategories
- Maintains backward compatibility with existing filtering

#### templates/includes/header.html
- Changed from hardcoded `[{"name":"Men"},{"name":"Women"},{"name":"Kids"}]`
- Now fetches from database: `frappe.db.get_all('Ecommerce Category')`
- Uses `item_group` field to link to existing category trees

#### templates/components/product_filter.html
- Removed hardcoded checks for 'Men', 'Women', 'Kids'
- Now works with any categories from the doctype
- Dynamic rendering based on category structure
- Maintains full filtering functionality

#### install_demo_data.py
- Updated demo products to car parts theme:
  - Premium Brake Pads
  - High-Flow Air Filter
  - All-Weather Floor Mats
- Demo products map to the new categories via item groups

## How It Works

### Category Hierarchy

```
Ecommerce Category (Database)
  ├── category_name: "Engine Parts"
  ├── display_name: "Engine Parts"
  ├── route_slug: "engine-parts"
  ├── item_group: "Men" (links to existing Item Group tree)
  └── enabled: 1

Item Group (ERPNext)
  └── Men (parent)
      ├── Subcategory 1
      ├── Subcategory 2
      └── Subcategory 3
```

The system uses a two-tier approach:
1. **Top Level:** Ecommerce Category (managed in database)
2. **Subcategories:** Item Group hierarchy (existing ERPNext functionality)

This allows:
- Easy customization of top-level categories
- Reuse of existing Item Group trees
- Backward compatibility with existing products

## Installation & Setup

### Fresh Installation

When installing ls_shop, the `after_install()` hook automatically:
1. Creates default payment modes
2. Creates ecommerce item groups
3. Creates ecommerce categories

### Existing Installation

To add categories to an existing installation:

```python
# In bench console
bench --site your-site-name console

# Then run:
from ls_shop.migrate import create_ecommerce_categories
create_ecommerce_categories()
```

### Running Demo Data

```bash
bench --site your-site-name execute ls_shop.install_demo_data.install_demo_data
```

This will create:
- 3 car parts themed products
- Ecommerce categories
- All necessary configurations

## Customization Guide

### Adding New Categories

1. Go to: **Lifestyle Shop Ecommerce > Ecommerce Category > New**

2. Fill in the fields:
   ```
   Category Name: Exterior Parts
   Display Name: Exterior Parts
   Route Slug: exterior-parts (auto-generated)
   Item Group: [Select existing Item Group or create new]
   Enabled: ✓
   Display Order: 4
   ```

3. Save

The new category will immediately appear in:
- Header navigation
- Product filters
- Category listings

### Renaming Existing Categories

The default categories (Engine Parts, Brake System, Interior Accessories) can be renamed:

1. Open the Ecommerce Category
2. Change `display_name` to your preferred name
3. Optionally update `route_slug`
4. Save

**Example:** Rename "Engine Parts" to "Performance Parts"
- This won't affect the underlying item group mapping
- Products will still filter correctly

### Changing Category Order

Update the `display_order` field:
- Lower numbers appear first
- Categories with same order are sorted alphabetically

### Disabling Categories

Uncheck `enabled` to temporarily hide a category without deleting it.

### Linking to Different Item Groups

Change the `item_group` field to map to different subcategory trees:

```
Engine Parts → Link to "Automotive" item group
Brake System → Link to "Safety Components" item group
```

## Testing Instructions

### 1. Test Category Creation

```python
# In bench console
import frappe

# Create test category
cat = frappe.get_doc({
    "doctype": "Ecommerce Category",
    "category_name": "Test Category",
    "display_name": "Test Category",
    "route_slug": "test-category",
    "enabled": 1,
    "display_order": 10
})
cat.insert()
frappe.db.commit()
```

**Expected Result:** Category appears in header navigation

### 2. Test Header Navigation

1. Visit `/products` page
2. Check header navigation shows categories from database
3. Verify category names match `display_name` field

**Expected:** Dynamic categories appear in correct order

### 3. Test Product Filtering

1. Go to `/products` page
2. Open filter sidebar
3. Verify categories are listed
4. Select a category filter
5. Verify products filter correctly

**Expected:** 
- Categories from Ecommerce Category doctype appear
- Subcategories from linked Item Groups load
- Filtering works correctly

### 4. Test Category Customization

1. Edit an Ecommerce Category
2. Change `display_name`
3. Change `display_order`
4. Save and refresh frontend

**Expected:** Changes reflect immediately (after cache clear)

### 5. Test Backward Compatibility

1. Verify existing products still display
2. Check old item group filters still work
3. Ensure category trees load correctly

**Expected:** No breaking changes to existing functionality

## API Methods

### Python API

```python
# Get all active categories
from ls_shop.lifestyle_shop_ecommerce.doctype.ecommerce_category.ecommerce_category import get_active_categories

categories = get_active_categories()
# Returns: [{"name": "...", "display_name": "...", "route_slug": "...", ...}]

# Get category by slug
from ls_shop.lifestyle_shop_ecommerce.doctype.ecommerce_category.ecommerce_category import get_category_by_slug

category = get_category_by_slug("engine-parts")
```

### Jinja Template Usage

```html
{% set categories = frappe.db.get_all('Ecommerce Category',
    {"enabled":1},
    fields=["name","display_name","route_slug"],
    order_by="display_order asc") %}

{% for category in categories %}
    <a href="/products?category={{ category.route_slug }}">
        {{ category.display_name }}
    </a>
{% endfor %}
```

## Migration Notes

### From Hardcoded to Dynamic

**Before:**
```python
parent_categories = [{"name":"Men"},{"name":"Women"},{"name":"Kids"}]
```

**After:**
```python
parent_categories = frappe.db.get_all('Ecommerce Category',
    {"enabled":1},
    fields=["name","display_name","route_slug","item_group"],
    order_by="display_order asc")
```

### Key Benefits

1. **No Code Changes Required** - Add/remove/modify categories through UI
2. **Multi-tenant Friendly** - Different sites can have different categories
3. **Customizable Order** - Control display order without code
4. **Icon Support** - Add icons/images to categories
5. **Easy Disable** - Temporarily hide categories
6. **SEO Friendly** - Custom route slugs for each category

## Troubleshooting

### Categories Not Showing

1. Check `enabled` field is checked
2. Verify `display_order` is set
3. Clear cache: `bench --site site-name clear-cache`
4. Check browser console for errors

### Filtering Not Working

1. Verify `item_group` field is set correctly
2. Check Item Group exists and has products
3. Ensure Item Group has `custom_display_on_website` enabled
4. Check console logs for filter state

### Route Slugs Conflict

1. Ensure `route_slug` is unique
2. System validates on save
3. Use frappe.scrub() format (lowercase-with-dashes)

## Future Enhancements

Potential additions:
- Multi-level category hierarchy within Ecommerce Category
- Category-specific banners and descriptions
- Category SEO meta tags
- Category images in navigation
- Category-specific sorting rules
- Featured products per category

## Support

For issues or questions:
1. Check error logs: **Error Log** in Frappe Desk
2. Review console logs in browser developer tools
3. Verify database queries in **Query Report**
4. Test with demo data for comparison

---

**Implementation Date:** 2025-10-03  
**Version:** 1.0.0  
**Compatibility:** Frappe v15+, ERPNext v15+