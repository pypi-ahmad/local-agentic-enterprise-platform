import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#0b111b",
        panel: "#101827",
        accent: "#00c29a",
        warning: "#ffb65e"
      }
    }
  },
  plugins: []
};

export default config;
