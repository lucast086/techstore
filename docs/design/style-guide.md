# TechStore Style Guide

## 📚 Complete Design System Documentation

Welcome to the TechStore Style Guide - your single source of truth for building consistent, beautiful, and accessible interfaces.

## Table of Contents

1. [Introduction](#introduction)
2. [Brand Guidelines](#brand-guidelines)
3. [Design Principles](#design-principles)
4. [Visual Language](#visual-language)
5. [Component Library](#component-library)
6. [Implementation Guide](#implementation-guide)
7. [Best Practices](#best-practices)
8. [Resources](#resources)

## Introduction

### Purpose
This style guide ensures consistency across all TechStore interfaces, speeds up development, and maintains our brand identity throughout the product.

### How to Use This Guide
- **Designers**: Reference visual specifications and component patterns
- **Developers**: Use code examples and implementation guidelines
- **Product Managers**: Understand design decisions and principles

### Living Document
This guide evolves with our product. Updates are versioned and communicated to all teams.

## Brand Guidelines

### Brand Personality
TechStore embodies five core traits:
- **Friendly & Approachable** - Easy to use, welcoming
- **Tech-Savvy & Modern** - Current without being trendy
- **Reliable & Trustworthy** - Consistent and dependable
- **Efficient & Fast** - Streamlined workflows
- **Simple & Minimalist** - Clean, uncluttered design

### Voice & Tone
- Clear and concise
- Professional yet friendly
- Helpful without being patronizing
- Action-oriented

### Logo Usage
```
Primary: [T] TechStore
Icon: [T] (standalone for small spaces)
```

Minimum clear space: 1x the height of the icon
Minimum size: 32px height

## Design Principles

### 1. Clarity First
Every element must have a clear purpose. Remove anything that doesn't directly help users accomplish their goals.

### 2. Consistency is Key
Use established patterns. When creating new patterns, ensure they align with existing ones.

### 3. Accessibility Always
Design for everyone. Meet WCAG 2.1 AA standards as a minimum.

### 4. Performance Matters
Beautiful design should never compromise speed. Optimize assets and interactions.

### 5. Data-Dense, Not Cluttered
Handle complex information elegantly. Use progressive disclosure and smart layouts.

## Visual Language

### Color System

#### Primary Palette
- **Primary Blue**: #2563EB - Main actions, links
- **Primary Hover**: #1D4ED8
- **Primary Light**: #DBEAFE - Backgrounds

#### Neutral Palette
- **Gray 900**: #111827 - Primary text
- **Gray 700**: #374151 - Secondary text
- **Gray 500**: #6B7280 - Muted text
- **Gray 300**: #D1D5DB - Borders
- **Gray 100**: #F3F4F6 - Backgrounds

#### Semantic Colors
- **Success**: #10B981 (Green)
- **Warning**: #F59E0B (Amber)
- **Error**: #EF4444 (Red)
- **Info**: #2563EB (Blue)
- **AI**: #8B5CF6 (Purple)

[View Complete Color Palette →](./color-palette.md)

### Typography

#### Font Stack
- **Primary**: Inter (UI text)
- **Monospace**: JetBrains Mono (codes, numbers)

#### Type Scale
- **Display**: 48px, 36px, 30px
- **Headings**: 24px, 20px, 18px, 16px, 14px
- **Body**: 18px, 16px, 14px, 12px

[View Typography System →](./typography-system.md)

### Spacing

Base unit: **4px**

Common values:
- 8px (small gaps)
- 16px (default spacing)
- 24px (section spacing)
- 32px (large gaps)

[View Spacing System →](./spacing-grid-system.md)

### Icons

Using **Heroicons** library:
- 24x24px base size
- 2px stroke weight
- Consistent geometric style

[View Icon System →](./icons-visual-assets.md)

## Component Library

### Buttons

#### Primary Button
```html
<button class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
  Primary Action
</button>
```

#### Secondary Button
```html
<button class="px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
  Secondary Action
</button>
```

### Forms

#### Input Field
```html
<div class="form-group">
  <label class="block text-sm font-medium text-gray-700 mb-2">
    Label
  </label>
  <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500">
  <p class="mt-1 text-sm text-gray-500">Help text</p>
</div>
```

### Tables

#### Data Table
```html
<table class="w-full">
  <thead>
    <tr>
      <th class="px-4 py-3 bg-gray-50 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
        Column
      </th>
    </tr>
  </thead>
  <tbody class="bg-white divide-y divide-gray-100">
    <tr class="hover:bg-gray-50">
      <td class="px-4 py-4">Data</td>
    </tr>
  </tbody>
</table>
```

[View All Components →](./component-patterns.md)

## Implementation Guide

### Getting Started

1. **Include Design Tokens**
   ```html
   <link rel="stylesheet" href="/static/css/design-tokens.css">
   ```

2. **Set Up Tailwind**
   ```javascript
   // tailwind.config.js
   module.exports = require('./tailwind.config.js');
   ```

3. **Use Semantic HTML**
   ```html
   <nav>, <main>, <article>, <section>
   ```

### File Structure
```
/static
  /css
    - design-tokens.css
    - components.css
  /js
    - design-tokens.js
  /fonts
    - Inter-*.woff2
```

### Naming Conventions
- **CSS Classes**: `kebab-case`
- **JavaScript**: `camelCase`
- **Components**: `PascalCase`
- **Files**: `kebab-case`

## Best Practices

### Do's
✅ Use design tokens for all values
✅ Test on multiple screen sizes
✅ Check color contrast
✅ Include focus states
✅ Write semantic HTML
✅ Optimize images
✅ Document deviations

### Don'ts
❌ Create one-off styles
❌ Use inline styles
❌ Ignore accessibility
❌ Mix design systems
❌ Skip responsive testing
❌ Forget loading states
❌ Override tokens locally

## Quick Reference

### Common Patterns

#### Page Layout
```html
<div class="min-h-screen bg-gray-50">
  <header class="bg-white border-b border-gray-200 h-16">
    <!-- Header content -->
  </header>
  <main class="container mx-auto px-4 py-8">
    <!-- Page content -->
  </main>
</div>
```

#### Card Component
```html
<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  <h3 class="text-lg font-semibold text-gray-900 mb-2">Title</h3>
  <p class="text-gray-600">Content</p>
</div>
```

#### Form Layout
```html
<form class="space-y-6">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Form fields -->
  </div>
  <div class="flex justify-end gap-4">
    <button type="button" class="btn btn-secondary">Cancel</button>
    <button type="submit" class="btn btn-primary">Save</button>
  </div>
</form>
```

## Resources

### Design Files
- [Figma Component Library](#)
- [Icon Set](#)
- [Prototypes](#)

### Development
- [GitHub Repository](https://github.com/techstore)
- [Component Storybook](#)
- [Design Tokens NPM](#)

### Documentation
1. [Brand Identity](./brand-identity.md)
2. [Color Palette](./color-palette.md)
3. [Typography System](./typography-system.md)
4. [Spacing & Grid](./spacing-grid-system.md)
5. [Component Patterns](./component-patterns.md)
6. [Interactive States](./interactive-states.md)
7. [Accessibility Standards](./accessibility-standards.md)
8. [Icons & Visual Assets](./icons-visual-assets.md)
9. [Design Tokens](./design-tokens.md)

### Live Examples
- [Color Preview](./color-preview.html)
- [Typography Preview](./typography-preview.html)
- [Spacing Preview](./spacing-preview.html)
- [Component Examples](./component-examples.html)
- [Interactive Demo](./interactive-demo.html)
- [Icons Demo](./icons-demo.html)

## Version History

### v1.0.0 (Current)
- Initial design system release
- Complete component library
- Accessibility standards
- Design token system

## Contact

For questions or suggestions about this style guide:
- Design Team: design@techstore.com
- Development: dev@techstore.com
- Slack: #design-system

---

*"Good design is as little design as possible."* - Dieter Rams

Remember: This guide helps us build better products faster. When in doubt, prioritize user needs and maintain consistency.