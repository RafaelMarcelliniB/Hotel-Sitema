/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1A237E',
        secondary: '#F9A825',
        accent: '#7C3AED',
        background: '#F8FAFC',
        surface: '#FFFFFF',
        success: '#0F9D58',
        warning: '#F59E0B',
        danger: '#D32F2F',
        neutral: '#64748B',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 12px 40px rgba(15, 23, 42, 0.08)',
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, #1A237E 0%, #312E81 45%, #F9A825 100%)',
      },
    },
  },
  plugins: [],
}

