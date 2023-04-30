import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/texas_api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/texas_api/, ''),
      },
      '/socket.io': {
        target: 'http://127.0.0.1:8000/socket.io',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/socket.io/, ''),
      }
    }
  }
})
