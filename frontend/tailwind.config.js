/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#FAF7F2",       // Elegant warm white/cream background
        cardBg: "#FFFFFF",       // Clean premium white cards
        borderLight: "#E5DCD3",   // Soft warm taupe borders
        accentBlue: "#B36A70",    // Dusty Rose primary accent
        accentGreen: "#8C9A86",   // Muted sage green for operational health
        accentOrange: "#C59A70",  // Muted warm gold for warnings
        accentRed: "#9C5257",     // Deep rose for critical status
        textMuted: "#A89F91"      // Warm Taupe secondary text
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "sans-serif"]
      }
    },
  },
  plugins: [],
}
