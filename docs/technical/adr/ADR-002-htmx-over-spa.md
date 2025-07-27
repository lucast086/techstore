# ADR-002: HTMX over SPA Framework

## Status
Accepted

## Context
TechStore needs a web interface that is:
- Easy to develop and maintain
- Fast and responsive
- Accessible to non-technical users
- SEO friendly for public-facing pages

Options considered:
- Single Page Application (React/Vue/Angular)
- Server-side rendering with progressive enhancement (HTMX)
- Traditional server-side rendering only
- Mobile-first with web as secondary

## Decision
We will use **HTMX with server-side rendering** via Jinja2 templates as the primary UI approach.

## Rationale

### Why HTMX:
1. **Simplicity**: No build step, no complex state management
2. **Performance**: Smaller payload, faster initial load
3. **SEO**: Natural server-side rendering
4. **Progressive Enhancement**: Works without JavaScript
5. **Developer Experience**: Backend developers can build UI
6. **Maintenance**: Less JavaScript complexity

### Why Not SPA:
1. **Complexity**: Requires separate frontend build pipeline
2. **Team Skills**: Team is backend-focused
3. **SEO Challenges**: Requires SSR setup
4. **Bundle Size**: Larger initial download
5. **State Management**: Additional complexity layer

### HTMX Implementation Strategy:
```html
<!-- Example: Dynamic search -->
<input type="text" 
       name="search" 
       hx-get="/customers/search" 
       hx-trigger="keyup changed delay:500ms" 
       hx-target="#search-results">

<div id="search-results">
  <!-- Server returns HTML partial -->
</div>
```

## Consequences

### Positive:
- Reduced complexity
- Faster development
- Better SEO
- Lower maintenance burden
- Unified backend/frontend codebase

### Negative:
- Less rich interactivity (acceptable for business app)
- Limited offline capabilities
- Fewer frontend developers familiar with approach
- Some modern UI patterns harder to implement

### Migration Options:
If SPA needed later:
1. Add React/Vue components for specific features
2. Build separate admin SPA while keeping HTMX for main app
3. Implement GraphQL layer for SPA consumption

## Implementation Guidelines

### Template Structure:
```
templates/
├── base.html           # Main layout
├── components/         # Reusable partials
│   ├── forms/
│   ├── tables/
│   └── modals/
└── pages/             # Full pages
    ├── customers/
    ├── products/
    └── repairs/
```

### HTMX Patterns:
- Use `hx-boost` for progressive form enhancement
- Implement `hx-indicator` for loading states
- Leverage `hx-swap` for smooth transitions
- Use Alpine.js for local state when needed

## References
- [HTMX Documentation](https://htmx.org)
- [Essay: The Market for Lemons](https://www.htmx.org/essays/a-market-for-lemons/)
- [When to Use HTMX](https://www.htmx.org/essays/when-to-use-hypermedia/)