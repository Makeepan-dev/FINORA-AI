/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        finora: {
          dark: '#0B0F19',
          card: '#111827',
          surface: '#1E293B',
          border: '#334155',
          primary: '#06B6D4', // cyan-500
          accent: '#10B981', // emerald-500
          warning: '#F59E0B',
          danger: '#EF4444',
          subtle: '#94A3B8',
          text: '#F8FAFC',
          purple: '#8B5CF6'
        }
      }
    },
  },
  plugins: [],
}
