/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0B0F19",       // Premium dark navy background
        cardBg: "#151C2C",       // Deep glassmorphic slate cards
        borderLight: "#222D44",   // Subtle card borders
        accentGreen: "#00E676",   // High-vis green for operational health
        accentOrange: "#FF9100",  // Warn alert status
        accentRed: "#FF5252",     // Critical alert status
        accentBlue: "#2979FF",    // Active info indicators
        textMuted: "#94A3B8"      // Cool gray text
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "sans-serif"]
      }
    },
  },
  plugins: [],
}
