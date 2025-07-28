# TechStore Spacing Quick Reference

## 🎯 Common Spacing Values

### Tailwind Classes
```
p-0   → 0px
p-0.5 → 2px     (micro adjustments)
p-1   → 4px     (tight)
p-2   → 8px     (compact)
p-3   → 12px    (comfortable)
p-4   → 16px    (default)
p-5   → 20px    
p-6   → 24px    (spacious)
p-8   → 32px    (very spacious)
p-10  → 40px
p-12  → 48px    (sections)
p-16  → 64px    (large sections)
```

## 📦 Component Recipes

### Card
```html
<!-- Default Card -->
<div class="bg-white rounded-lg border border-gray-300 p-6">
  <!-- 24px padding -->
</div>

<!-- Compact Card -->
<div class="bg-white rounded-lg border border-gray-300 p-4">
  <!-- 16px padding -->
</div>
```

### Button
```html
<!-- Default -->
<button class="px-4 py-2 bg-primary-500 text-white rounded">
  <!-- 16px horizontal, 8px vertical -->
</button>

<!-- Small -->
<button class="px-3 py-1.5 text-sm">
  <!-- 12px horizontal, 6px vertical -->
</button>

<!-- Large -->
<button class="px-6 py-3 text-lg">
  <!-- 24px horizontal, 12px vertical -->
</button>
```

### Form
```html
<div class="space-y-6"> <!-- 24px gap between groups -->
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">
      <!-- 8px margin below label -->
    </label>
    <input class="w-full px-3 py-2 border rounded">
      <!-- 12px horizontal, 8px vertical padding -->
    <p class="mt-1 text-sm text-gray-500">
      <!-- 4px margin above help text -->
    </p>
  </div>
</div>
```

### Page Layout
```html
<!-- Header -->
<header class="h-16 px-4 lg:px-8 flex items-center">
  <!-- 64px height, responsive padding -->
</header>

<!-- Main with Sidebar -->
<div class="flex">
  <aside class="w-sidebar p-6">
    <!-- 256px width, 24px padding -->
  </aside>
  <main class="flex-1 p-6 lg:p-8">
    <!-- Responsive padding -->
  </main>
</div>

<!-- Content Sections -->
<section class="py-12 lg:py-16">
  <!-- 48px mobile, 64px desktop -->
</section>
```

### Grid Layouts
```html
<!-- Card Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- 24px gap -->
</div>

<!-- Tight Grid -->
<div class="grid grid-cols-4 gap-4">
  <!-- 16px gap -->
</div>

<!-- Section Grid -->
<div class="space-y-12">
  <!-- 48px vertical spacing between sections -->
</div>
```

## 📱 Responsive Patterns

### Container
```html
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <!-- 16px → 24px → 32px padding -->
</div>
```

### Section Padding
```html
<section class="py-8 md:py-12 lg:py-16">
  <!-- 32px → 48px → 64px vertical -->
</section>
```

### Component Spacing
```html
<div class="mb-4 md:mb-6 lg:mb-8">
  <!-- 16px → 24px → 32px margin -->
</div>
```

## 🎨 Visual Hierarchy

### Text Spacing
- Headings: `mb-4` to `mb-6` (16-24px below)
- Paragraphs: `mb-4` (16px between)
- Lists: `space-y-2` (8px between items)
- Sections: `mb-12` (48px between major sections)

### Component Grouping
- Related: `space-y-2` or `space-y-3` (8-12px)
- Distinct: `space-y-4` or `space-y-6` (16-24px)
- Sections: `space-y-12` (48px)

## ⚡ Quick Tips

1. **Start with defaults**: p-4, gap-6, space-y-4
2. **Mobile first**: Increase spacing on larger screens
3. **Be consistent**: Use the same spacing for similar components
4. **Group related**: Less space between related items
5. **Test touch targets**: Minimum 44x44px on mobile