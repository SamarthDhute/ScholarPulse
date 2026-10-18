/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        page: "var(--bg-page)",
        surface: "var(--bg-surface)",
        "surface-muted": "var(--surface-muted)",
        "primary-text": "var(--text-primary)",
        "secondary-text": "var(--text-secondary)",
        border: "var(--border-color)",
        blue: {
          primary: "var(--primary-blue)",
          hover: "var(--blue-hover)",
          active: "var(--blue-active)",
          pale: "var(--pale-blue)",
        },
        status: {
          success: "var(--status-success)",
          "success-bg": "var(--status-success-bg)",
          warning: "var(--status-warning)",
          "warning-bg": "var(--status-warning-bg)",
          error: "var(--status-error)",
          "error-bg": "var(--status-error-bg)",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        focus: "var(--shadow-focus)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
      },
    },
  },
  plugins: [],
}
