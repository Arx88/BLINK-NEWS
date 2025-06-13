// news-blink-frontend/vite.config.js
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Cargar variables de entorno de Docker
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: '0.0.0.0', // Importante para que sea accesible desde fuera del contenedor
      port: 5173,
      proxy: {
        '/api': {
          // Usar la variable de entorno, o localhost si no está definida
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:5000',
          changeOrigin: true,
        }
      }
    },
  }
})