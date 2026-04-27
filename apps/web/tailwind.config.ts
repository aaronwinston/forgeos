import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          purple: 'var(--accent)',
        },
        fg: {
          primary:   'var(--fg-primary)',
          secondary: 'var(--fg-secondary)',
          tertiary:  'var(--fg-tertiary)',
        },
        bg: {
          primary:   'var(--bg-primary)',
          secondary: 'var(--bg-secondary)',
          tertiary:  'var(--bg-tertiary)',
        },
        border:  'var(--border)',
        success: 'var(--success)',
        warning: 'var(--warning)',
        error:   'var(--error)',
        accent:  'var(--accent)',
      },
      borderRadius: {
        card:  '8px',
        input: '6px',
        chip:  '4px',
      },
      fontFamily: {
        display: ['Fraunces', 'serif'],
        sans:    ['Inter', 'sans-serif'],
      },
      keyframes: {
        shimmer: {
          '0%':   { opacity: '0.6' },
          '50%':  { opacity: '1' },
          '100%': { opacity: '0.6' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
export default config;
