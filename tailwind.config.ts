import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#07111f",
        panel: "#0c1728",
        accent: "#22d3ee",
        pulse: "#34d399",
        line: "rgba(148, 163, 184, 0.18)"
      },
      fontFamily: {
        sans: ["Avenir Next", "Segoe UI", "Helvetica Neue", "Arial", "sans-serif"]
      },
      boxShadow: {
        panel: "0 24px 70px rgba(4, 9, 24, 0.45)",
        glow: "0 0 0 1px rgba(34, 211, 238, 0.18), 0 0 40px rgba(34, 211, 238, 0.12)"
      },
      backgroundImage: {
        "hero-grid":
          "linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px)"
      }
    }
  },
  plugins: []
};

export default config;
