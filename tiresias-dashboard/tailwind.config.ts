import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'hsl(0, 0%, 8%)',
        foreground: 'hsl(0, 0%, 98%)',

        primary: {
          DEFAULT: 'hsl(210, 100%, 60%)',
          foreground: 'hsl(0, 0%, 100%)',
        },

        secondary: {
          DEFAULT: 'hsl(210, 10%, 25%)',
          foreground: 'hsl(0, 0%, 98%)',
        },

        accent: {
          DEFAULT: 'hsl(150, 60%, 50%)',
          foreground: 'hsl(0, 0%, 10%)',
        },

        destructive: {
          DEFAULT: 'hsl(0, 85%, 60%)',
          foreground: 'hsl(0, 0%, 98%)',
        },

        border: 'hsl(210, 10%, 30%)',
        input: 'hsl(210, 10%, 25%)',
        ring: 'hsl(210, 100%, 60%)',
      },

      ringWidth: {
        DEFAULT: '3px',
      },

      ringOffsetWidth: {
        DEFAULT: '2px',
      },

      spacing: {
        touch: '44px',
      },

      fontFamily: {
        sans: [
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        mono: ['SF Mono', 'Monaco', 'Inconsolata', 'monospace'],
      },

      fontSize: {
        xs: '0.875rem',
        sm: '1rem',
        base: '1.125rem',
        lg: '1.25rem',
        xl: '1.5rem',
        '2xl': '2rem',
        '3xl': '2.5rem',
      },

      keyframes: {
        'focus-ring': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },

      animation: {
        'focus-ring': 'focus-ring 1.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};

export default config;
