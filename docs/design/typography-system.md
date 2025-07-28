# TechStore Typography System

## 🔤 Typography Philosophy
Clear hierarchy, optimal readability, and consistent rhythm across all interfaces.

## Font Stack

### Primary Font Family
**Inter** - Modern, highly legible, designed for UI
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
```

### Monospace Font Family
**For code, numbers, IDs**
```css
font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
```

## Type Scale

### Display (Marketing/Landing)
- `display-lg`: 3rem/48px - Line height: 1.2 - Weight: 600
- `display-md`: 2.25rem/36px - Line height: 1.3 - Weight: 600
- `display-sm`: 1.875rem/30px - Line height: 1.3 - Weight: 600

### Headings (Application)
- `heading-xl`: 1.5rem/24px - Line height: 1.4 - Weight: 600
- `heading-lg`: 1.25rem/20px - Line height: 1.4 - Weight: 600
- `heading-md`: 1.125rem/18px - Line height: 1.5 - Weight: 600
- `heading-sm`: 1rem/16px - Line height: 1.5 - Weight: 600
- `heading-xs`: 0.875rem/14px - Line height: 1.5 - Weight: 600

### Body Text
- `body-lg`: 1.125rem/18px - Line height: 1.75 - Weight: 400
- `body-md`: 1rem/16px - Line height: 1.5 - Weight: 400 (Default)
- `body-sm`: 0.875rem/14px - Line height: 1.5 - Weight: 400
- `body-xs`: 0.75rem/12px - Line height: 1.5 - Weight: 400

### Special Text
- `label`: 0.875rem/14px - Line height: 1.5 - Weight: 500 - Letter spacing: 0.025em
- `caption`: 0.75rem/12px - Line height: 1.5 - Weight: 400
- `overline`: 0.75rem/12px - Line height: 1.5 - Weight: 600 - Letter spacing: 0.05em - Uppercase

## Font Weights
- `300`: Light (rarely used)
- `400`: Regular (body text)
- `500`: Medium (labels, emphasis)
- `600`: Semibold (headings)
- `700`: Bold (strong emphasis)

## Text Colors
Based on our color palette:
- **Primary Text**: `gray-900` (#111827)
- **Secondary Text**: `gray-700` (#374151)
- **Muted Text**: `gray-500` (#6B7280)
- **Placeholder**: `gray-400` (#9CA3AF)
- **Link Text**: `primary-500` (#2563EB)
- **Link Hover**: `primary-600` (#1D4ED8)

## Usage Guidelines

### Page Hierarchy
```
Page Title (heading-xl)
├── Section Title (heading-lg)
│   ├── Subsection (heading-md)
│   └── Card Title (heading-sm)
        └── Field Label (label)
            └── Help Text (body-sm + muted)
```

### Data Tables
- **Table Header**: `label` + `gray-700` + uppercase
- **Table Cell**: `body-md` + `gray-900`
- **Numeric Data**: `monospace` + `body-md`

### Forms
- **Field Label**: `label` + `gray-700`
- **Input Text**: `body-md` + `gray-900`
- **Placeholder**: `body-md` + `gray-400`
- **Help Text**: `body-sm` + `gray-500`
- **Error Text**: `body-sm` + `error-500`

### Cards & Lists
- **Card Title**: `heading-md` + `gray-900`
- **List Item**: `body-md` + `gray-900`
- **Metadata**: `body-sm` + `gray-500`

### Buttons
- **Primary Button**: `body-md` + `500` weight
- **Secondary Button**: `body-md` + `500` weight
- **Text Button**: `body-md` + `500` weight + underline on hover

## Responsive Typography

### Mobile Adjustments
```css
/* Mobile (< 640px) */
@media (max-width: 639px) {
  .heading-xl { font-size: 1.25rem; }
  .heading-lg { font-size: 1.125rem; }
  .display-lg { font-size: 2rem; }
  .display-md { font-size: 1.5rem; }
}
```

## Line Length
- **Optimal**: 45-75 characters per line
- **Maximum**: 80 characters for body text
- **Minimum**: 20 characters before wrapping

## Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    fontFamily: {
      'sans': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      'mono': ['JetBrains Mono', 'SF Mono', 'Monaco', 'monospace'],
    },
    fontSize: {
      // Body sizes
      'xs': ['0.75rem', { lineHeight: '1.5' }],
      'sm': ['0.875rem', { lineHeight: '1.5' }],
      'base': ['1rem', { lineHeight: '1.5' }],
      'lg': ['1.125rem', { lineHeight: '1.75' }],
      
      // Heading sizes
      'xl': ['1.25rem', { lineHeight: '1.4' }],
      '2xl': ['1.5rem', { lineHeight: '1.4' }],
      
      // Display sizes
      '3xl': ['1.875rem', { lineHeight: '1.3' }],
      '4xl': ['2.25rem', { lineHeight: '1.3' }],
      '5xl': ['3rem', { lineHeight: '1.2' }],
    },
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
    letterSpacing: {
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
    },
  },
};
```

## CSS Variables

```css
:root {
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Monaco, monospace;
  
  /* Font Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;
  
  /* Line Heights */
  --leading-tight: 1.2;
  --leading-snug: 1.3;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
  
  /* Letter Spacing */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
}
```

## Implementation Notes

### Font Loading Strategy
```html
<!-- Preconnect to font provider -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Load Inter with display swap -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Optional: Load JetBrains Mono for code -->
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Performance Considerations
1. Use `font-display: swap` for better perceived performance
2. Subset fonts to only needed characters/weights
3. Consider system font stack fallback for faster initial load
4. Use variable fonts if supporting modern browsers

### Accessibility
- Maintain minimum 16px for body text
- Ensure sufficient contrast (follow color palette guidelines)
- Use relative units (rem) for scalability
- Test with browser zoom at 200%
- Avoid fonts weights below 400 for body text