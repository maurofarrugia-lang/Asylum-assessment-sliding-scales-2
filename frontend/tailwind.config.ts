import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          ink: '#16324F',
          slate: '#5C6B7A',
          mist: '#EAF0F6',
          line: '#C7D2DD',
          accent: '#24577A',
          warn: '#8A5A00',
          danger: '#8B1E3F',
          success: '#1D5F4A'
        }
      }
    },
  },
  plugins: [],
};

export default config;
