# LS Shop Customization Guide

Complete guide to customizing your LS Shop ecommerce store appearance and content.

## Overview

LS Shop provides extensive customization options through **Lifestyle Settings**, allowing you to:
- Configure branding (logos, favicons, store name)
- Customize footer content and links
- Set contact information
- Configure social media links
- Change color scheme across the entire site

## Accessing Customization Settings

1. Log in to ERPNext
2. Search for **Lifestyle Settings** in the Awesome Bar
3. Open the **Lifestyle Settings** doctype

## Customization Sections

### 1. Branding (Main Tab)

**Fields:**
- **Store Name** - Displayed in browser tab and throughout site
- **Brand Logo** - Header navigation logo (uploads as image)
  - Displays at: 48×48px square (maintains aspect ratio)
  - Best size: ~200×200px
- **Footer Logo** - Logo shown in footer
  - Mobile: 48×128px max
  - Desktop: 64×160px max
  - Best size: ~250×80px
- **Favicon** - Browser tab icon
  - Recommended: 32×32px or 16×16px .ico/.png file

### 2. Contact Information Tab

**Fields:**
- **Contact Phone** - Phone number displayed in footer
- **Contact Email** - Email address displayed in footer  
- **Working Hours** - Business hours text

**Example:**
```
Contact Phone: +1 (555) 123-4567
Contact Email: support@mystore.com
Working Hours: Mon - Fri / 9:00 AM - 5:00 PM
```

### 3. Social Media Tab

**Fields:**
- **Facebook URL** - Full URL to your Facebook page
- **Twitter/X URL** - Full URL to your Twitter/X profile
- **Instagram URL** - Full URL to your Instagram profile
- **Snapchat URL** - Full URL to your Snapchat profile
- **TikTok URL** - Full URL to your TikTok profile

**Notes:**
- Leave empty to hide that social icon
- Icons only appear if URLs are provided
- Opens in new tab with security attributes

### 4. Footer Customization Tab

#### Newsletter Section
- **Newsletter Title** - Heading for newsletter signup
- **Newsletter Description** - Text explaining newsletter benefits

#### Footer Assets
- **Payment Methods Image** - Image showing accepted payment methods
  - Default: Shows credit cards, mobile payments
- **VAT Certificate Image** - Tax compliance certificate/badge
  - Optional, leave empty to hide

#### Copyright & Legal
- **Copyright Text** - Footer copyright notice
  - Default: "Lifestyle. All Rights Reserved"
  - Example: "© 2025 My Store. All Rights Reserved"

#### Footer Sections
**Flexible footer link organization** using child table:

**Structure:**
```
Footer Section
├── Section Title (e.g., "My Account")
├── Display Order (controls position)
├── Enabled (show/hide section)
└── Footer Links (child table)
    ├── Link Label
    ├── Link URL
    ├── Display Order
    └── Enabled
```

**Default Sections Created:**
1. **My Account** - Account-related links
2. **Policies** - Legal/policy pages
3. **Customer Service** - Support links

**To Add Custom Section:**
1. Click "Add Row" in Footer Sections table
2. Set Section Title (e.g., "About Us")
3. Set Display Order (1, 2, 3...)
4. Check "Enabled"
5. Add links in the Footer Links sub-table

**To Edit Links:**
1. Expand a footer section row
2. Modify links in the Footer Links table
3. Set Link Label and Link URL
4. Order links with Display Order field

### 5. Color Scheme Tab

**Primary Colors:**
- **Primary Color** - Main brand color (buttons, CTAs)
  - Default: `#b91c1c` (red-800)
  - Used in: Buttons, badges, key actions
- **Primary Hover Color** - Hover state for primary elements
  - Default: `#991b1b` (red-900)

**Link Colors:**
- **Link Color** - Text links and clickable elements
  - Default: `#7f1d1d` (red-950)
- **Link Hover Color** - Link hover state
  - Default: `#991b1b` (red-900)

**Accent Colors:**
- **Accent Color** - Discount badges, notifications
  - Default: `#b91c1c` (red-800)
- **Border Accent Color** - Border highlights
  - Default: `#b91c1c` (red-800)

**Footer Colors:**
- **Footer Background Color** - Footer background
  - Default: `#111827` (gray-900)
- **Footer Text Color** - Footer text
  - Default: `#ffffff` (white)

## How Color System Works

### CSS Custom Properties
Colors are converted to CSS variables and injected into every page:

```css
:root {
  --ls-primary: #b91c1c;
  --ls-primary-hover: #991b1b;
  --ls-link: #7f1d1d;
  /* ... etc */
}
```

### Utility Classes
Templates use these utility classes that map to your colors:

| Class | Purpose | CSS Variable |
|-------|---------|--------------|
| `.bg-primary` | Primary background | `--ls-primary` |
| `.text-primary` | Primary text | `--ls-primary` |
| `.hover:bg-primary-hover` | Hover background | `--ls-primary-hover` |
| `.text-link` | Link text | `--ls-link` |
| `.hover:text-link-hover` | Link hover | `--ls-link-hover` |
| `.bg-accent` | Accent background | `--ls-accent` |
| `.bg-footer` | Footer background | `--ls-footer-bg` |
| `.text-footer` | Footer text | `--ls-footer-text` |

### Where Colors Are Applied

**Primary Color:**
- Add to cart buttons
- Proceed to checkout buttons
- Apply filters buttons
- Login/signup buttons
- Action buttons

**Link Color:**
- Product brand names
- Category navigation
- Footer links
- Text links

**Accent Color:**
- Discount badges ("17% off")
- Sale notifications
- Wishlist count badges

**Footer Colors:**
- Footer background and all footer text

## Step-by-Step Customization

### Example: Changing to Blue Theme

1. Open **Lifestyle Settings**
2. Go to **Color Scheme** tab
3. Set colors:
   - Primary Color: `#1e40af` (blue-800)
   - Primary Hover: `#1e3a8a` (blue-900)
   - Link Color: `#1e3a8a` (blue-900)
   - Link Hover: `#1d4ed8` (blue-700)
   - Accent Color: `#2563eb` (blue-600)
4. Save settings
5. Clear cache: `bench --site your-site clear-cache`
6. Refresh browser

### Example: Custom Footer Sections

**Add "About Us" Section:**
1. Go to **Footer Customization** tab
2. Scroll to **Footer Sections** table
3. Click "Add Row"
4. Fill in:
   - Section Title: "About Us"
   - Section Order: 4
   - Enabled: ✓
5. In the row, expand **Footer Links**
6. Add links:
   - Label: "Our Story", URL: "/about", Order: 1
   - Label: "Team", URL: "/team", Order: 2
   - Label: "Careers", URL: "/careers", Order: 3
7. Save

## Testing Your Changes

After making changes:

```bash
# 1. Migrate database (if doctypes changed)
bench --site your-site migrate

# 2. Clear cache (always required)
bench --site your-site clear-cache

# 3. Reload browser with hard refresh
# Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

## Advanced: Product Images

Product images come from **Style Attribute Variant** → **Website Slideshow Item**:

1. Open **Style Attribute Variant** list
2. Select a variant (e.g., "BRAKE-PADS-Black")
3. Scroll to **Images** section
4. Add images:
   - First image (idx=1) shows in product listings
   - Additional images appear in product detail carousel
5. Upload or paste image URLs

## Troubleshooting

**Colors not applying:**
- Clear browser cache (Ctrl+Shift+Del)
- Run: `bench --site your-site clear-cache`
- Check Color Scheme tab has colors filled in

**Footer sections not showing:**
- Verify sections are Enabled
- Check Display Order is set
- Ensure at least one link per section is Enabled
- Clear cache and reload

**Social icons missing:**
- Provide full URLs (https://facebook.com/yourpage)
- Save and clear cache
- Icons only show if URL is provided

**Images too large:**
- Header logo: constrained to 48×48px
- Footer logo: constrained to 64×160px max
- Images auto-scale with `object-contain`
- Aspect ratio always preserved

## Best Practices

1. **Colors:**
   - Use color picker or hex codes (#rrggbb)
   - Test on both light and dark backgrounds
   - Ensure sufficient contrast for accessibility

2. **Footer Links:**
   - Use relative URLs for internal pages (/about)
   - Use absolute URLs for external sites (https://...)
   - Order logically (most important first)

3. **Images:**
   - Optimize images before upload (WebP format recommended)
   - Use transparent PNGs for logos
   - Favicon should be square

4. **Contact Info:**
   - Use international format for phone
   - Test email links work
   - Keep working hours clear and concise

## Files Modified

This customization system modified:
- [`lifestyle_settings.json`](development-bench/apps/ls_shop/ls_shop/lifestyle_shop_ecommerce/doctype/lifestyle_settings/lifestyle_settings.json) - Added ~25 fields
- [`lifestyle_settings.py`](development-bench/apps/ls_shop/ls_shop/lifestyle_shop_ecommerce/doctype/lifestyle_settings/lifestyle_settings.py) - CSS generator
- [`footer_section_config`](development-bench/apps/ls_shop/ls_shop/lifestyle_shop_ecommerce/doctype/footer_section_config/) - New doctype
- [`footer_link`](development-bench/apps/ls_shop/ls_shop/lifestyle_shop_ecommerce/doctype/footer_link/) - New doctype
- [`layout.html`](development-bench/apps/ls_shop/ls_shop/templates/layout.html) - CSS injection
- [`footer.html`](development-bench/apps/ls_shop/ls_shop/templates/includes/footer.html) - Dynamic rendering
- [`social_links.html`](development-bench/apps/ls_shop/ls_shop/templates/includes/social_links.html) - Dynamic URLs
- [`header.html`](development-bench/apps/ls_shop/ls_shop/templates/includes/header.html) - Dynamic logo
- Various templates - Color class updates

## Support

For issues or questions:
1. Check this guide first
2. Review [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation
3. Check [DEMO_DATA_README.md](DEMO_DATA_README.md) for demo data
4. Review [ECOMMERCE_CATEGORY_IMPLEMENTATION.md](ECOMMERCE_CATEGORY_IMPLEMENTATION.md) for categories