/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4A1F2B',     // Deep Burgundy
        secondary: '#B47A32',   // Burnt Ochre
        accent: '#3F6F68',      // Muted Teal
        background: '#F4F0E8',  // Warm Ivory
        surface: '#FFFCF5',     // Surface
        text: '#292625',        // Charcoal
        'muted-text': '#6F6964', // Muted Text
        border: '#D8D0C5',      // Border
        success: '#5F7048',     // Olive
        warning: '#B47A32',     // Burnt Ochre
        critical: '#9B3D32',    // Brick
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
