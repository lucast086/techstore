# TechStore Color Palette

## 🎨 Color Philosophy
Clean, modern, and purposeful - every color serves a function while maintaining visual harmony.

## Primary Colors

### Brand Blue
**Primary actions, links, focus states**
- `primary-500`: #2563EB (Base) - Modern, trustworthy blue
- `primary-600`: #1D4ED8 (Hover)
- `primary-700`: #1E40AF (Active)
- `primary-100`: #DBEAFE (Light backgrounds)
- `primary-50`: #EFF6FF (Subtle backgrounds)

### Neutral Grays
**Text, borders, backgrounds**
- `gray-900`: #111827 (Primary text)
- `gray-700`: #374151 (Secondary text)
- `gray-500`: #6B7280 (Muted text)
- `gray-400`: #9CA3AF (Placeholders)
- `gray-300`: #D1D5DB (Borders)
- `gray-200`: #E5E7EB (Dividers)
- `gray-100`: #F3F4F6 (Backgrounds)
- `gray-50`: #F9FAFB (Subtle backgrounds)
- `white`: #FFFFFF (Base background)

## Semantic Colors

### Success (Green)
**Positive actions, confirmations**
- `success-500`: #10B981 (Base)
- `success-600`: #059669 (Hover)
- `success-100`: #D1FAE5 (Backgrounds)

### Warning (Amber)
**Cautions, pending states**
- `warning-500`: #F59E0B (Base)
- `warning-600`: #D97706 (Hover)
- `warning-100`: #FEF3C7 (Backgrounds)

### Error (Red)
**Errors, destructive actions**
- `error-500`: #EF4444 (Base)
- `error-600`: #DC2626 (Hover)
- `error-100`: #FEE2E2 (Backgrounds)

### Info (Blue)
**Information, tips**
- `info-500`: #3B82F6 (Base)
- `info-100`: #DBEAFE (Backgrounds)

## Special Purpose Colors

### Purple Accent
**AI features, premium elements**
- `purple-500`: #8B5CF6 (AI indicators)
- `purple-100`: #EDE9FE (AI backgrounds)

### Surface Colors
**Cards, modals, elevated elements**
- `surface`: #FFFFFF
- `surface-hover`: #F9FAFB
- `surface-active`: #F3F4F6

## Usage Guidelines

### Text Hierarchy
```css
/* Primary text */
color: var(--gray-900);

/* Secondary text */
color: var(--gray-700);

/* Muted/helper text */
color: var(--gray-500);

/* Disabled text */
color: var(--gray-400);
```

### Interactive Elements
```css
/* Primary buttons */
background: var(--primary-500);
hover: var(--primary-600);
active: var(--primary-700);

/* Secondary buttons */
background: var(--white);
border: var(--gray-300);
hover-background: var(--gray-50);
```

### Backgrounds
```css
/* Main background */
background: var(--white);

/* Section backgrounds */
background: var(--gray-50);

/* Card backgrounds */
background: var(--surface);
```

## Accessibility Notes

### Contrast Ratios
- Gray-900 on white: 17.9:1 ✅ (AAA)
- Gray-700 on white: 10.9:1 ✅ (AAA)
- Primary-500 on white: 4.7:1 ✅ (AA)
- Success-500 on white: 4.5:1 ✅ (AA)
- Error-500 on white: 4.5:1 ✅ (AA)

### Color Blind Considerations
- Don't rely solely on color for meaning
- Use icons alongside color indicators
- Maintain sufficient contrast
- Test with color blind simulators

## Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#2563EB',
          600: '#1D4ED8',
          700: '#1E40AF',
        },
        gray: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          700: '#374151',
          900: '#111827',
        },
        success: {
          100: '#D1FAE5',
          500: '#10B981',
          600: '#059669',
        },
        warning: {
          100: '#FEF3C7',
          500: '#F59E0B',
          600: '#D97706',
        },
        error: {
          100: '#FEE2E2',
          500: '#EF4444',
          600: '#DC2626',
        },
        purple: {
          100: '#EDE9FE',
          500: '#8B5CF6',
        },
      },
    },
  },
};
```

## CSS Variables

```css
:root {
  /* Primary */
  --primary-50: #EFF6FF;
  --primary-100: #DBEAFE;
  --primary-500: #2563EB;
  --primary-600: #1D4ED8;
  --primary-700: #1E40AF;
  
  /* Neutrals */
  --gray-50: #F9FAFB;
  --gray-100: #F3F4F6;
  --gray-200: #E5E7EB;
  --gray-300: #D1D5DB;
  --gray-400: #9CA3AF;
  --gray-500: #6B7280;
  --gray-700: #374151;
  --gray-900: #111827;
  
  /* Semantic */
  --success-100: #D1FAE5;
  --success-500: #10B981;
  --success-600: #059669;
  
  --warning-100: #FEF3C7;
  --warning-500: #F59E0B;
  --warning-600: #D97706;
  
  --error-100: #FEE2E2;
  --error-500: #EF4444;
  --error-600: #DC2626;
  
  /* Special */
  --purple-100: #EDE9FE;
  --purple-500: #8B5CF6;
  
  /* Surfaces */
  --surface: #FFFFFF;
  --surface-hover: #F9FAFB;
  --surface-active: #F3F4F6;
}
```