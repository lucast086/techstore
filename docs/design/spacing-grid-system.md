# TechStore Spacing & Grid System

## 📏 Spacing Philosophy
Consistent, mathematical spacing that creates visual rhythm and enhances usability.

## Base Unit
**4px** - All spacing values are multiples of 4px for consistency and alignment.

## Spacing Scale

### Core Scale (0-12)
```
0:   0px    (0rem)     - No space
0.5: 2px    (0.125rem) - Hairline
1:   4px    (0.25rem)  - Micro
2:   8px    (0.5rem)   - Tiny
3:   12px   (0.75rem)  - Small
4:   16px   (1rem)     - Base
5:   20px   (1.25rem)  - Medium
6:   24px   (1.5rem)   - Large
8:   32px   (2rem)     - XL
10:  40px   (2.5rem)   - 2XL
12:  48px   (3rem)     - 3XL
```

### Extended Scale (16-96)
```
16:  64px   (4rem)     - 4XL
20:  80px   (5rem)     - 5XL
24:  96px   (6rem)     - 6XL
32:  128px  (8rem)     - Section gaps
40:  160px  (10rem)    - Large sections
48:  192px  (12rem)    - Hero sections
64:  256px  (16rem)    - Extra large
80:  320px  (20rem)    - Jumbo
96:  384px  (24rem)    - Maximum
```

## Grid System

### Container Widths
```css
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem; /* Mobile: 16px */
}

/* Breakpoints */
@media (min-width: 640px) {  /* sm */
  .container { 
    max-width: 640px;
    padding: 0 1.5rem; /* 24px */
  }
}

@media (min-width: 768px) {  /* md */
  .container { max-width: 768px; }
}

@media (min-width: 1024px) { /* lg */
  .container { 
    max-width: 1024px;
    padding: 0 2rem; /* 32px */
  }
}

@media (min-width: 1280px) { /* xl */
  .container { max-width: 1280px; }
}

@media (min-width: 1536px) { /* 2xl */
  .container { max-width: 1536px; }
}
```

### Grid Columns
- **12-column grid** for flexibility
- **Gap**: 24px (1.5rem) default
- **Responsive**: Collapses intelligently on mobile

```css
.grid {
  display: grid;
  gap: 1.5rem; /* 24px */
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
.grid-cols-6 { grid-template-columns: repeat(6, 1fr); }
.grid-cols-12 { grid-template-columns: repeat(12, 1fr); }
```

## Component Spacing Patterns

### Cards
```css
.card {
  padding: 1.5rem; /* 24px - default */
  border-radius: 0.5rem; /* 8px */
  margin-bottom: 1rem; /* 16px between cards */
}

.card-compact { padding: 1rem; }    /* 16px */
.card-spacious { padding: 2rem; }   /* 32px */
```

### Forms
```css
.form-group {
  margin-bottom: 1.5rem; /* 24px between fields */
}

.form-label {
  margin-bottom: 0.5rem; /* 8px */
}

.form-help {
  margin-top: 0.25rem; /* 4px */
}

.form-section {
  margin-bottom: 2rem; /* 32px between sections */
}
```

### Buttons
```css
.btn {
  padding: 0.5rem 1rem; /* 8px 16px - default */
  gap: 0.5rem; /* 8px between icon and text */
}

.btn-sm { padding: 0.375rem 0.75rem; }  /* 6px 12px */
.btn-lg { padding: 0.75rem 1.5rem; }    /* 12px 24px */
```

### Navigation
```css
.nav {
  padding: 1rem 0; /* 16px vertical */
  gap: 2rem; /* 32px between items */
}

.nav-item {
  padding: 0.5rem 1rem; /* 8px 16px */
}

.sidebar {
  width: 16rem; /* 256px */
  padding: 1.5rem; /* 24px */
}
```

### Tables
```css
.table th,
.table td {
  padding: 0.75rem 1rem; /* 12px 16px */
}

.table-compact th,
.table-compact td {
  padding: 0.5rem 0.75rem; /* 8px 12px */
}
```

## Page Layout Patterns

### Dashboard Layout
```
┌─────────────────────────────────────┐
│ Header (h: 64px, py: 16px)         │
├─────────┬───────────────────────────┤
│ Sidebar │ Main Content              │
│ (256px) │ (fluid, p: 24-32px)      │
│         │                           │
└─────────┴───────────────────────────┘
```

### Content Pages
```
┌─────────────────────────────────────┐
│ Page Header (py: 32px)              │
├─────────────────────────────────────┤
│ Content (max-w: 1280px, px: 16-32px)│
│ Sections (mb: 48px)                 │
│ Cards (gap: 24px)                   │
└─────────────────────────────────────┘
```

### Modal Spacing
```css
.modal {
  padding: 1.5rem; /* 24px */
  max-width: 32rem; /* 512px - default */
}

.modal-header { margin-bottom: 1rem; }     /* 16px */
.modal-body { margin-bottom: 1.5rem; }     /* 24px */
.modal-footer { gap: 0.75rem; }            /* 12px between buttons */
```

## Responsive Spacing

### Mobile-First Approach
```css
/* Base (mobile) */
.section { padding: 2rem 1rem; }    /* 32px 16px */

/* Tablet (768px+) */
@media (min-width: 768px) {
  .section { padding: 3rem 1.5rem; } /* 48px 24px */
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .section { padding: 4rem 2rem; }   /* 64px 32px */
}
```

### Spacing Utilities
```css
/* Margin */
.m-0 { margin: 0; }
.m-1 { margin: 0.25rem; }
.m-2 { margin: 0.5rem; }
.m-4 { margin: 1rem; }
.m-6 { margin: 1.5rem; }
.m-8 { margin: 2rem; }

/* Padding */
.p-0 { padding: 0; }
.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }

/* Directional */
.mt-4 { margin-top: 1rem; }
.mb-4 { margin-bottom: 1rem; }
.px-4 { padding-left: 1rem; padding-right: 1rem; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
```

## Visual Rhythm Guidelines

### Vertical Rhythm
- **Line height**: 1.5 for body text
- **Paragraph spacing**: 1rem (16px)
- **Section spacing**: 3rem (48px) minimum
- **Component spacing**: 1.5rem (24px) default

### Horizontal Rhythm
- **Container padding**: 16px → 24px → 32px (responsive)
- **Column gaps**: 24px (1.5rem) default
- **Inline spacing**: 8px (0.5rem) for related items

### Density Modes
```css
/* Default - Comfortable */
.density-normal {
  --spacing-unit: 1rem;
}

/* Compact - More content visible */
.density-compact {
  --spacing-unit: 0.75rem;
}

/* Comfortable - More breathing room */
.density-comfortable {
  --spacing-unit: 1.25rem;
}
```

## Implementation Notes

### CSS Custom Properties
```css
:root {
  /* Base unit */
  --space-unit: 4px;
  
  /* Scale */
  --space-0: 0;
  --space-0-5: 2px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;
  
  /* Component spacing */
  --card-padding: var(--space-6);
  --section-gap: var(--space-12);
  --form-gap: var(--space-6);
  --button-padding-x: var(--space-4);
  --button-padding-y: var(--space-2);
}
```

### Best Practices
1. **Consistency**: Always use scale values, avoid arbitrary spacing
2. **Proximity**: Related items closer, unrelated items farther
3. **Hierarchy**: More space = more separation = different sections
4. **Responsiveness**: Increase spacing on larger screens
5. **Accessibility**: Ensure touch targets are at least 44x44px

### Don'ts
- ❌ Don't use arbitrary pixel values (e.g., 17px, 23px)
- ❌ Don't mix spacing units (stick to rem/px consistently)
- ❌ Don't make touch targets too small on mobile
- ❌ Don't forget responsive spacing adjustments
- ❌ Don't use excessive spacing that wastes screen space