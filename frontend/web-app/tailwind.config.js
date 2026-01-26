import baseConfig from '../../config/tailwind.config.base.js'

/** @type {import('tailwindcss').Config} */
export default {
<<<<<<<< HEAD:ui/web/tailwind.config.js
  content: ['./index.html', './app/**/*.{js,ts,jsx,tsx}'],
========
  ...baseConfig,
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
>>>>>>>> 1017ee5d6165b6b836bcf8f4a86dd3b8c5d9a8a4:frontend/web-app/tailwind.config.js
  theme: {
    ...baseConfig.theme,
    extend: {
      ...(baseConfig.theme?.extend || {}),
      colors: {
        ink: '#1e293b',
        brand: {
          base: '#4f46e5',
          deep: '#312e81',
          soft: '#e0e7ff',
          accent: '#d97706',
        },
        bg: {
          main: '#f8fafc',
          card: '#ffffff',
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
}
