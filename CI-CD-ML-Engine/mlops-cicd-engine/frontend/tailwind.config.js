/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0B0E14",
        surface: "#11151D",
        raised: "#171C26",
        line: "#232936",
        ink: "#E7E9EE",
        muted: "#838D9E",
        signal: "#F5A623",   // running / attention
        link: "#5B8DEF",     // secondary accent
        success: "#3ECF8E",
        danger: "#F0546A",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset",
      },
      keyframes: {
        pulse_dot: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.35 },
        },
      },
      animation: {
        pulse_dot: "pulse_dot 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
