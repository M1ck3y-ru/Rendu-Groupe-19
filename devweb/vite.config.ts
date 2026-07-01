import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'https://profane-swoosh-ragged.ngrok-free.dev',
        changeOrigin: true,
        secure: false,
      },
      '/ollama-status': {
        target: 'https://profane-swoosh-ragged.ngrok-free.dev',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/ollama-status/, ''),
      }
    }
  }
})
