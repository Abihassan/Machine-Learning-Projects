import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // Must match backend/.env's ALLOWED_ORIGINS (CORS) — the backend only
    // accepts WebSocket/API requests from this exact origin by default.
    port: 5173,
  },
})
