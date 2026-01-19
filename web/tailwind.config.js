/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#111827',
        brand: {
          base: '#1e3a8a',
          deep: '#10275c',
          soft: '#e8edfb',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', '"Cairo"', 'sans-serif'],
        sans: ['"Cairo"', '"Inter"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 10px 40px rgba(17,24,39,0.12)',
      },
      borderRadius: {
        xl: '1.25rem',
      },
    },
  },
  plugins: [],
};
