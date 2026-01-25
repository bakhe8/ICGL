/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#1e293b', // Slate 800
        brand: {
          base: '#4f46e5', // Indigo 600
          deep: '#312e81', // Indigo 900
          soft: '#e0e7ff', // Indigo 100
          accent: '#d97706', // Amber 600
        },
        bg: {
          main: '#f8fafc',
          card: '#ffffff'
        }
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
