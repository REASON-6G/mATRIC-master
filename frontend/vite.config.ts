import { TanStackRouterVite } from "@tanstack/router-vite-plugin"
import react from "@vitejs/plugin-react-swc"
import legacy from "@vitejs/plugin-legacy"
import { defineConfig } from "vite"

import dotenv from "dotenv"

dotenv.config()
// https://vitejs.dev/config/
const apiBaseUrl = process.env.VITE_API_URL
const port = parseInt(process.env.VITE_PORT, 10) || 5173
const useLegacy = process.env.VITE_USE_LEGACY === "true"
const mapboxToken = process.env.VITE_MAPBOX_TOKEN
const mapboxStyle = process.env.VITE_MAPBOX_STYLE
export default defineConfig({
  plugins: [
      react(),
      useLegacy && legacy({
          targets: ["defaults", "not IE 11"],
      }),
      TanStackRouterVite()].filter(Boolean),
  define: {
        "process.env": {
            VITE_API_URL: JSON.stringify(apiBaseUrl),
            VITE_PORT: JSON.stringify(port),
            VITE_MAPBOX_TOKEN: JSON.stringify(mapboxToken),
            VITE_MAPBOX_STYLE: JSON.stringify(mapboxStyle),
        },
  },
  build: {
      sourcemap: process.env.VITE_SOURCEMAP === "true",
      outDir: process.env.VITE_OUT_DIR || "dist",
    },
})
