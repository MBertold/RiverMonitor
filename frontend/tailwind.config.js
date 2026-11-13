/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        allerta: {
          verde: "#10b981",
          giallo: "#f59e0b",
          arancione: "#f97316",
          rosso: "#ef4444",
        }
      }
    },
  },
  plugins: [],
}
