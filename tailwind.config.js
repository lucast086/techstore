/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/app/templates/**/*.html", "./src/app/static/**/*.js"],
  theme: {
    extend: {
      // Color System
      colors: {
        primary: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          500: "#2563EB",
          600: "#1D4ED8",
          700: "#1E40AF",
        },
        gray: {
          50: "#F9FAFB",
          100: "#F3F4F6",
          200: "#E5E7EB",
          300: "#D1D5DB",
          400: "#9CA3AF",
          500: "#6B7280",
          700: "#374151",
          900: "#111827",
        },
        success: {
          100: "#D1FAE5",
          500: "#10B981",
          600: "#059669",
        },
        warning: {
          100: "#FEF3C7",
          500: "#F59E0B",
          600: "#D97706",
        },
        error: {
          100: "#FEE2E2",
          500: "#EF4444",
          600: "#DC2626",
        },
        purple: {
          100: "#EDE9FE",
          500: "#8B5CF6",
        },
      },

      // Typography System
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: ["JetBrains Mono", "SF Mono", "Monaco", "monospace"],
      },

      fontSize: {
        // Body sizes
        xs: ["0.75rem", { lineHeight: "1.5" }],
        sm: ["0.875rem", { lineHeight: "1.5" }],
        base: ["1rem", { lineHeight: "1.5" }],
        lg: ["1.125rem", { lineHeight: "1.75" }],

        // Heading sizes
        xl: ["1.25rem", { lineHeight: "1.4" }],
        "2xl": ["1.5rem", { lineHeight: "1.4" }],

        // Display sizes
        "3xl": ["1.875rem", { lineHeight: "1.3" }],
        "4xl": ["2.25rem", { lineHeight: "1.3" }],
        "5xl": ["3rem", { lineHeight: "1.2" }],
      },

      fontWeight: {
        light: "300",
        normal: "400",
        medium: "500",
        semibold: "600",
        bold: "700",
      },

      letterSpacing: {
        tight: "-0.025em",
        normal: "0",
        wide: "0.025em",
        wider: "0.05em",
      },

      // Spacing System - Base unit: 4px
      spacing: {
        // Micro adjustments
        0.5: "0.125rem", // 2px

        // Extended scale
        18: "4.5rem", // 72px
        88: "22rem", // 352px
        120: "30rem", // 480px

        // Layout specific
        sidebar: "16rem", // 256px - Sidebar width
        header: "4rem", // 64px - Header height
        container: "80rem", // 1280px - Max container
      },

      // Grid Gap Values
      gap: {
        card: "1.5rem", // 24px - Card grids
        form: "1.5rem", // 24px - Form fields
        section: "3rem", // 48px - Page sections
      },

      // Border Radius
      borderRadius: {
        sm: "0.25rem", // 4px
        DEFAULT: "0.375rem", // 6px
        md: "0.5rem", // 8px
        lg: "0.75rem", // 12px
        xl: "1rem", // 16px
        "2xl": "1.5rem", // 24px
      },

      // Shadows
      boxShadow: {
        xs: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
        sm: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        DEFAULT:
          "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
        lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
        xl: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
      },

      // Animations
      animation: {
        "spin-slow": "spin 3s linear infinite",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
