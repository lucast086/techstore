/**
 * TechStore Design Tokens - JavaScript Export
 * Auto-generated from design system
 * DO NOT EDIT DIRECTLY
 */

export const tokens = {
  color: {
    // Blue scale
    blue: {
      50: "#EFF6FF",
      100: "#DBEAFE",
      200: "#BFDBFE",
      300: "#93C5FD",
      400: "#60A5FA",
      500: "#2563EB",
      600: "#1D4ED8",
      700: "#1E40AF",
      800: "#1E3A8A",
      900: "#1E3A8A",
    },
    // Gray scale
    gray: {
      50: "#F9FAFB",
      100: "#F3F4F6",
      200: "#E5E7EB",
      300: "#D1D5DB",
      400: "#9CA3AF",
      500: "#6B7280",
      600: "#4B5563",
      700: "#374151",
      800: "#1F2937",
      900: "#111827",
    },
    // Green scale
    green: {
      50: "#F0FDF4",
      100: "#D1FAE5",
      500: "#10B981",
      600: "#059669",
      700: "#047857",
    },
    // Amber scale
    amber: {
      50: "#FFFBEB",
      100: "#FEF3C7",
      500: "#F59E0B",
      600: "#D97706",
      700: "#B45309",
    },
    // Red scale
    red: {
      50: "#FEF2F2",
      100: "#FEE2E2",
      500: "#EF4444",
      600: "#DC2626",
      700: "#B91C1C",
    },
    // Purple scale
    purple: {
      50: "#FAF5FF",
      100: "#EDE9FE",
      500: "#8B5CF6",
      600: "#7C3AED",
      700: "#6D28D9",
    },
  },

  // Semantic colors
  semantic: {
    primary: "#2563EB",
    primaryHover: "#1D4ED8",
    primaryActive: "#1E40AF",
    primaryLight: "#DBEAFE",
    primaryLighter: "#EFF6FF",

    textPrimary: "#111827",
    textSecondary: "#374151",
    textMuted: "#6B7280",
    textPlaceholder: "#9CA3AF",
    textInverse: "#FFFFFF",

    background: "#FFFFFF",
    backgroundSubtle: "#F9FAFB",
    backgroundMuted: "#F3F4F6",

    border: "#D1D5DB",
    borderHover: "#9CA3AF",
    borderFocus: "#2563EB",

    success: "#10B981",
    successLight: "#D1FAE5",
    successDark: "#047857",

    warning: "#F59E0B",
    warningLight: "#FEF3C7",
    warningDark: "#B45309",

    error: "#EF4444",
    errorLight: "#FEE2E2",
    errorDark: "#B91C1C",

    info: "#2563EB",
    infoLight: "#DBEAFE",
    infoDark: "#1E40AF",

    ai: "#8B5CF6",
    aiLight: "#EDE9FE",
    aiDark: "#6D28D9",
  },

  // Typography
  font: {
    family: {
      sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      mono: "'JetBrains Mono', 'SF Mono', Monaco, monospace",
    },
    size: {
      xs: "0.75rem", // 12px
      sm: "0.875rem", // 14px
      base: "1rem", // 16px
      lg: "1.125rem", // 18px
      xl: "1.25rem", // 20px
      "2xl": "1.5rem", // 24px
      "3xl": "1.875rem", // 30px
      "4xl": "2.25rem", // 36px
      "5xl": "3rem", // 48px
    },
    weight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.2,
      snug: 1.3,
      normal: 1.5,
      relaxed: 1.75,
    },
    letterSpacing: {
      tight: "-0.025em",
      normal: "0",
      wide: "0.025em",
      wider: "0.05em",
    },
  },

  // Spacing
  space: {
    0: "0",
    0.5: "0.125rem", // 2px
    1: "0.25rem", // 4px
    2: "0.5rem", // 8px
    3: "0.75rem", // 12px
    4: "1rem", // 16px
    5: "1.25rem", // 20px
    6: "1.5rem", // 24px
    8: "2rem", // 32px
    10: "2.5rem", // 40px
    12: "3rem", // 48px
    16: "4rem", // 64px
    20: "5rem", // 80px
    24: "6rem", // 96px
    32: "8rem", // 128px
    40: "10rem", // 160px
    48: "12rem", // 192px
    56: "14rem", // 224px
    64: "16rem", // 256px
  },

  // Border radius
  radius: {
    none: "0",
    sm: "0.25rem", // 4px
    base: "0.375rem", // 6px
    md: "0.5rem", // 8px
    lg: "0.75rem", // 12px
    xl: "1rem", // 16px
    "2xl": "1.5rem", // 24px
    full: "9999px",
  },

  // Border width
  borderWidth: {
    0: "0",
    1: "1px",
    2: "2px",
    4: "4px",
    8: "8px",
  },

  // Shadows
  shadow: {
    xs: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    sm: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
    base: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
    md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
    xl: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
    "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
    inner: "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)",
    none: "none",
  },

  // Animation
  transition: {
    duration: {
      instant: "0ms",
      fast: "150ms",
      base: "200ms",
      slow: "300ms",
      slower: "500ms",
    },
    timing: {
      linear: "linear",
      ease: "ease",
      easeIn: "cubic-bezier(0.4, 0, 1, 1)",
      easeOut: "cubic-bezier(0, 0, 0.2, 1)",
      easeInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
      spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
    },
  },

  // Component-specific tokens
  button: {
    padding: {
      x: {
        sm: "0.75rem",
        base: "1rem",
        lg: "1.5rem",
      },
      y: {
        sm: "0.375rem",
        base: "0.5rem",
        lg: "0.75rem",
      },
    },
    fontSize: {
      sm: "0.875rem",
      base: "1rem",
      lg: "1.125rem",
    },
  },

  form: {
    input: {
      paddingX: "0.75rem",
      paddingY: "0.5rem",
      borderRadius: "0.5rem",
      fontSize: "1rem",
    },
    label: {
      fontSize: "0.875rem",
      fontWeight: 500,
      marginBottom: "0.5rem",
    },
  },

  card: {
    padding: {
      sm: "1rem",
      base: "1.5rem",
      lg: "2rem",
    },
    borderRadius: "0.75rem",
  },
};

/**
 * Get a token value by path
 * @param {string} path - Dot notation path (e.g., 'color.primary')
 * @returns {any} Token value
 */
export function getToken(path) {
  return path.split(".").reduce((obj, key) => obj?.[key], tokens);
}

/**
 * Apply tokens to CSS custom properties
 */
export function applyTokensToCSS() {
  const root = document.documentElement;

  // Apply color tokens
  Object.entries(tokens.semantic).forEach(([key, value]) => {
    const cssKey = key.replace(/([A-Z])/g, "-$1").toLowerCase();
    root.style.setProperty(`--color-${cssKey}`, value);
  });

  // Apply spacing tokens
  Object.entries(tokens.space).forEach(([key, value]) => {
    root.style.setProperty(`--space-${key}`, value);
  });

  // Apply font sizes
  Object.entries(tokens.font.size).forEach(([key, value]) => {
    root.style.setProperty(`--text-${key}`, value);
  });
}

// Export for use in other modules
export default tokens;
