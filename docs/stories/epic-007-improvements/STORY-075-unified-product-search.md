# STORY-075: Unified Product Search Experience

**Status:** Draft
**Priority:** P1 (High)
**Type:** UX Improvement
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a user, when I search for products in the catalog (/products), I want the search to work exactly like in POS - with inline real-time results instead of opening a modal.

## Current State
- **POS**: Inline search with live results via HTMX (good UX)
- **Catalog**: Opens modal for search (poor UX, extra clicks)

## Desired State
- Both POS and Catalog use same inline search pattern
- Consistent search experience across the application
- Real-time results without modal interruption

## Acceptance Criteria
- [ ] Remove search modal from products catalog
- [ ] Implement inline search field like POS
- [ ] Results appear below search field in real-time
- [ ] Search by: name, SKU, barcode (same as POS)
- [ ] Maintain existing filters (category, stock status)
- [ ] Click on result navigates to product detail
- [ ] 300ms debounce for performance
- [ ] Loading indicator during search
- [ ] "No results" message when appropriate

## Technical Implementation

### Files to Modify
- `/src/app/templates/products/list.html` - Replace modal with inline search
- `/src/app/templates/products/_search_results.html` - Results template
- `/src/app/web/products.py` - Search endpoint if needed
- `/src/app/static/js/products.js` - Remove modal JavaScript
- **Delete**: Modal-related files if they exist

### Tasks
- [ ] Study POS search implementation
- [ ] Remove modal HTML and JavaScript
- [ ] Implement inline search input with HTMX
- [ ] Create/adapt search results template
- [ ] Ensure search endpoint returns proper HTML
- [ ] Add loading spinner
- [ ] Style results consistently with POS
- [ ] Test search functionality
- [ ] Remove unused modal code

### Implementation Template
```html
<!-- New implementation in products/list.html -->
<div class="search-container">
    <label for="product-search" class="block text-sm font-medium text-gray-700">
        Buscar Productos
    </label>
    <div class="mt-1 relative">
        <input type="text"
               id="product-search"
               name="q"
               class="w-full px-4 py-2 border rounded-lg"
               placeholder="Buscar por nombre, SKU o código de barras..."
               hx-get="/products/search"
               hx-trigger="keyup changed delay:300ms"
               hx-target="#search-results"
               hx-indicator="#search-spinner">

        <div id="search-spinner" class="htmx-indicator">
            <svg class="animate-spin h-5 w-5">...</svg>
        </div>
    </div>

    <div id="search-results" class="mt-4">
        <!-- Results will be loaded here -->
    </div>
</div>
```

## Testing Requirements
- Search for products by name
- Search by SKU
- Search by barcode
- Verify 300ms debounce works
- Test with no results
- Test with many results
- Click result → navigate to detail
- Verify filters still work alongside search

## Migration Notes
- Ensure no broken links to modal
- Update any documentation mentioning modal
- Clean up unused CSS for modal
- Remove modal event listeners

## Dev Notes
- Consider extracting search component for reuse
- Ensure consistent styling between POS and catalog
- May need to adjust endpoint response format
- Consider pagination for many results

---

## Dev Agent Record

### Task Progress
- [ ] Remove modal implementation
- [ ] Add inline search field
- [ ] Implement HTMX attributes
- [ ] Create results template
- [ ] Test search functionality
- [ ] Clean up unused code

### Debug Log

### Completion Notes

### File List

### Change Log

### Agent Model Used
