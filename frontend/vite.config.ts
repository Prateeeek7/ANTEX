import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all interfaces for Docker
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000', // Use Docker service name
        changeOrigin: true,
      },
    },
  },
})
