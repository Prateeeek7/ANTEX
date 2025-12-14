/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Professional Coolors Palette
        primary: {
          dark: '#3a606e',    // Dark teal - primary dark
          DEFAULT: '#607b7d',  // Medium teal - primary
          light: '#7a9ba0',   // Light teal variant
        },
        secondary: {
          dark: '#6b7a6b',    // Dark sage variant
          DEFAULT: '#828e82',  // Sage green - secondary
          light: '#9ba89b',   // Light sage variant
        },
        accent: {
          DEFAULT: '#aaae8e', // Light sage/beige - accent
          light: '#c4c8b0',   // Very light accent
        },
        neutral: {
          50: '#f5f6f5',
          100: '#e8ebe8',
          200: '#d1d6d1',
          300: '#b8c0b8',
          400: '#9fa99f',
          500: '#828e82',
          600: '#6b7a6b',
          700: '#556055',
          800: '#3a606e',
          900: '#2d4a55',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(58, 96, 110, 0.08), 0 10px 20px -2px rgba(58, 96, 110, 0.04)',
        'medium': '0 4px 20px -2px rgba(58, 96, 110, 0.12), 0 8px 16px -4px rgba(58, 96, 110, 0.08)',
        'strong': '0 10px 30px -5px rgba(58, 96, 110, 0.2), 0 15px 25px -5px rgba(58, 96, 110, 0.1)',
      },
    },
  },
  plugins: [],
}


