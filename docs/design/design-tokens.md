# TechStore Design Tokens

## 🔧 Design Token Philosophy
Single source of truth for all design decisions. Update once, reflect everywhere.

## Token Structure

Design tokens are organized in three tiers:
1. **Primitive Tokens**: Raw values (colors, sizes)
2. **Semantic Tokens**: Meaningful aliases (primary, secondary)
3. **Component Tokens**: Component-specific values

## Color Tokens

### Primitive Colors
```json
{
  "color": {
    "blue": {
      "50": "#EFF6FF",
      "100": "#DBEAFE",
      "200": "#BFDBFE",
      "300": "#93C5FD",
      "400": "#60A5FA",
      "500": "#2563EB",
      "600": "#1D4ED8",
      "700": "#1E40AF",
      "800": "#1E3A8A",
      "900": "#1E3A8A"
    },
    "gray": {
      "50": "#F9FAFB",
      "100": "#F3F4F6",
      "200": "#E5E7EB",
      "300": "#D1D5DB",
      "400": "#9CA3AF",
      "500": "#6B7280",
      "600": "#4B5563",
      "700": "#374151",
      "800": "#1F2937",
      "900": "#111827"
    },
    "green": {
      "50": "#F0FDF4",
      "100": "#D1FAE5",
      "200": "#A7F3D0",
      "300": "#6EE7B7",
      "400": "#34D399",
      "500": "#10B981",
      "600": "#059669",
      "700": "#047857",
      "800": "#065F46",
      "900": "#064E3B"
    },
    "amber": {
      "50": "#FFFBEB",
      "100": "#FEF3C7",
      "200": "#FDE68A",
      "300": "#FCD34D",
      "400": "#FBBF24",
      "500": "#F59E0B",
      "600": "#D97706",
      "700": "#B45309",
      "800": "#92400E",
      "900": "#78350F"
    },
    "red": {
      "50": "#FEF2F2",
      "100": "#FEE2E2",
      "200": "#FECACA",
      "300": "#FCA5A5",
      "400": "#F87171",
      "500": "#EF4444",
      "600": "#DC2626",
      "700": "#B91C1C",
      "800": "#991B1B",
      "900": "#7F1D1D"
    },
    "purple": {
      "50": "#FAF5FF",
      "100": "#EDE9FE",
      "200": "#DDD6FE",
      "300": "#C4B5FD",
      "400": "#A78BFA",
      "500": "#8B5CF6",
      "600": "#7C3AED",
      "700": "#6D28D9",
      "800": "#5B21B6",
      "900": "#4C1D95"
    }
  }
}
```

### Semantic Colors
```json
{
  "semantic": {
    "primary": "{color.blue.500}",
    "primary-hover": "{color.blue.600}",
    "primary-active": "{color.blue.700}",
    "primary-light": "{color.blue.100}",
    "primary-lighter": "{color.blue.50}",
    
    "text-primary": "{color.gray.900}",
    "text-secondary": "{color.gray.700}",
    "text-muted": "{color.gray.500}",
    "text-placeholder": "{color.gray.400}",
    "text-inverse": "#FFFFFF",
    
    "background": "#FFFFFF",
    "background-subtle": "{color.gray.50}",
    "background-muted": "{color.gray.100}",
    
    "border": "{color.gray.300}",
    "border-hover": "{color.gray.400}",
    "border-focus": "{semantic.primary}",
    
    "success": "{color.green.500}",
    "success-light": "{color.green.100}",
    "success-dark": "{color.green.700}",
    
    "warning": "{color.amber.500}",
    "warning-light": "{color.amber.100}",
    "warning-dark": "{color.amber.700}",
    
    "error": "{color.red.500}",
    "error-light": "{color.red.100}",
    "error-dark": "{color.red.700}",
    
    "info": "{color.blue.500}",
    "info-light": "{color.blue.100}",
    "info-dark": "{color.blue.700}",
    
    "ai": "{color.purple.500}",
    "ai-light": "{color.purple.100}",
    "ai-dark": "{color.purple.700}"
  }
}
```

## Typography Tokens

### Font Families
```json
{
  "font": {
    "family": {
      "sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      "mono": "'JetBrains Mono', 'SF Mono', Monaco, monospace"
    },
    "size": {
      "xs": "0.75rem",      // 12px
      "sm": "0.875rem",     // 14px
      "base": "1rem",       // 16px
      "lg": "1.125rem",     // 18px
      "xl": "1.25rem",      // 20px
      "2xl": "1.5rem",      // 24px
      "3xl": "1.875rem",    // 30px
      "4xl": "2.25rem",     // 36px
      "5xl": "3rem"         // 48px
    },
    "weight": {
      "light": 300,
      "normal": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700
    },
    "lineHeight": {
      "tight": 1.2,
      "snug": 1.3,
      "normal": 1.5,
      "relaxed": 1.75
    },
    "letterSpacing": {
      "tight": "-0.025em",
      "normal": "0",
      "wide": "0.025em",
      "wider": "0.05em"
    }
  }
}
```

## Spacing Tokens

### Space Scale
```json
{
  "space": {
    "0": "0",
    "0.5": "0.125rem",    // 2px
    "1": "0.25rem",       // 4px
    "2": "0.5rem",        // 8px
    "3": "0.75rem",       // 12px
    "4": "1rem",          // 16px
    "5": "1.25rem",       // 20px
    "6": "1.5rem",        // 24px
    "8": "2rem",          // 32px
    "10": "2.5rem",       // 40px
    "12": "3rem",         // 48px
    "16": "4rem",         // 64px
    "20": "5rem",         // 80px
    "24": "6rem",         // 96px
    "32": "8rem",         // 128px
    "40": "10rem",        // 160px
    "48": "12rem",        // 192px
    "56": "14rem",        // 224px
    "64": "16rem"         // 256px
  }
}
```

## Size Tokens

### Border Radius
```json
{
  "radius": {
    "none": "0",
    "sm": "0.25rem",      // 4px
    "base": "0.375rem",   // 6px
    "md": "0.5rem",       // 8px
    "lg": "0.75rem",      // 12px
    "xl": "1rem",         // 16px
    "2xl": "1.5rem",      // 24px
    "full": "9999px"
  }
}
```

### Border Width
```json
{
  "border": {
    "width": {
      "0": "0",
      "1": "1px",
      "2": "2px",
      "4": "4px",
      "8": "8px"
    }
  }
}
```

## Shadow Tokens

```json
{
  "shadow": {
    "xs": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    "sm": "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
    "base": "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
    "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
    "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
    "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
    "inner": "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
    "none": "none"
  }
}
```

## Animation Tokens

```json
{
  "transition": {
    "duration": {
      "instant": "0ms",
      "fast": "150ms",
      "base": "200ms",
      "slow": "300ms",
      "slower": "500ms"
    },
    "timing": {
      "linear": "linear",
      "ease": "ease",
      "ease-in": "cubic-bezier(0.4, 0, 1, 1)",
      "ease-out": "cubic-bezier(0, 0, 0.2, 1)",
      "ease-in-out": "cubic-bezier(0.4, 0, 0.2, 1)",
      "spring": "cubic-bezier(0.34, 1.56, 0.64, 1)"
    }
  }
}
```

## Component Tokens

### Button Tokens
```json
{
  "button": {
    "padding": {
      "x": {
        "sm": "{space.3}",
        "base": "{space.4}",
        "lg": "{space.6}"
      },
      "y": {
        "sm": "{space.1.5}",
        "base": "{space.2}",
        "lg": "{space.3}"
      }
    },
    "fontSize": {
      "sm": "{font.size.sm}",
      "base": "{font.size.base}",
      "lg": "{font.size.lg}"
    },
    "borderRadius": "{radius.md}",
    "fontWeight": "{font.weight.medium}"
  }
}
```

### Form Tokens
```json
{
  "form": {
    "input": {
      "padding": {
        "x": "{space.3}",
        "y": "{space.2}"
      },
      "borderRadius": "{radius.md}",
      "borderWidth": "{border.width.1}",
      "fontSize": "{font.size.base}",
      "lineHeight": "{font.lineHeight.normal}"
    },
    "label": {
      "fontSize": "{font.size.sm}",
      "fontWeight": "{font.weight.medium}",
      "marginBottom": "{space.2}"
    },
    "help": {
      "fontSize": "{font.size.sm}",
      "marginTop": "{space.1}"
    },
    "group": {
      "marginBottom": "{space.6}"
    }
  }
}
```

### Card Tokens
```json
{
  "card": {
    "padding": {
      "sm": "{space.4}",
      "base": "{space.6}",
      "lg": "{space.8}"
    },
    "borderRadius": "{radius.lg}",
    "borderWidth": "{border.width.1}",
    "shadow": "{shadow.sm}"
  }
}
```

## CSS Variables Implementation

```css
:root {
  /* Color Primitives */
  --color-blue-50: #EFF6FF;
  --color-blue-100: #DBEAFE;
  --color-blue-500: #2563EB;
  --color-blue-600: #1D4ED8;
  --color-blue-700: #1E40AF;
  
  /* Semantic Colors */
  --color-primary: var(--color-blue-500);
  --color-primary-hover: var(--color-blue-600);
  --color-primary-light: var(--color-blue-100);
  
  /* Typography */
  --font-sans: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  
  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  
  /* Animation */
  --duration-fast: 150ms;
  --duration-base: 200ms;
  --timing-ease-out: cubic-bezier(0, 0, 0.2, 1);
}
```

## JavaScript/TypeScript Tokens

```typescript
// tokens.ts
export const tokens = {
  color: {
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
      // ... etc
    }
  },
  space: {
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    // ... etc
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    // ... etc
  }
} as const;

// Helper function
export function token(path: string): string {
  return path.split('.').reduce((obj, key) => obj[key], tokens);
}

// Usage
const primaryColor = token('color.primary.500'); // '#2563EB'
```

## Tailwind Integration

```javascript
// tailwind.config.js
const tokens = require('./design-tokens.json');

module.exports = {
  theme: {
    extend: {
      colors: tokens.color,
      spacing: tokens.space,
      fontSize: tokens.font.size,
      fontWeight: tokens.font.weight,
      borderRadius: tokens.radius,
      boxShadow: tokens.shadow,
    }
  }
}
```

## Token Usage Guidelines

### Do's
- ✅ Always use tokens instead of hard-coded values
- ✅ Use semantic tokens over primitive tokens
- ✅ Create component-specific tokens when needed
- ✅ Document token additions/changes
- ✅ Keep tokens organized and consistent

### Don'ts
- ❌ Don't create one-off tokens
- ❌ Don't mix token systems
- ❌ Don't override tokens locally
- ❌ Don't use arbitrary values
- ❌ Don't break the token hierarchy

## Token Management

### Adding New Tokens
1. Add to appropriate category
2. Use consistent naming
3. Reference existing tokens when possible
4. Update documentation
5. Test across all platforms

### Deprecating Tokens
1. Mark as deprecated
2. Provide migration path
3. Update all usages
4. Remove after grace period
5. Document in changelog

## Platform-Specific Exports

### Web (CSS)
```bash
npm run tokens:css
# Outputs: tokens.css
```

### React Native
```bash
npm run tokens:rn
# Outputs: tokens.js
```

### Figma
```bash
npm run tokens:figma
# Outputs: tokens.json (Figma Tokens format)
```

## Token Validation

```javascript
// validate-tokens.js
const requiredTokens = [
  'color.primary',
  'color.text-primary',
  'space.4',
  'font.size.base'
];

function validateTokens(tokens) {
  requiredTokens.forEach(path => {
    if (!getToken(tokens, path)) {
      throw new Error(`Missing required token: ${path}`);
    }
  });
}
```

## Benefits

1. **Consistency**: Same values everywhere
2. **Maintainability**: Update in one place
3. **Scalability**: Easy to add new platforms
4. **Documentation**: Self-documenting design
5. **Automation**: Generate platform-specific code
6. **Validation**: Ensure design compliance
7. **Version Control**: Track design changes