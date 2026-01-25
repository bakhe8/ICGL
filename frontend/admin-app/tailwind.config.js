import baseConfig from '../../config/tailwind.config.base.js'

/** @type {import('tailwindcss').Config} */
export default {
  ...baseConfig,
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    ...baseConfig.theme,
    extend: {
      ...(baseConfig.theme?.extend || {}),
    },
  },
}
