import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/auth": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
      "/access": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
      "/inventory": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
      "/sales": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
      "/settings": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
      "/media": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
      "/reports": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
      "/procurement": {
        target: process.env.VITE_PROXY_API_TARGET || "http://backend:8000",
        changeOrigin: true,
      },
    },
    allowedHosts: [
      "www.pacashollywood.storeorange.ovh",
      "pacashollywood.storeorange.ovh",
    ],
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules/apexcharts") || id.includes("node_modules/vue3-apexcharts")) {
            return "charts";
          }
          if (id.includes("node_modules/primevue") || id.includes("node_modules/@primeuix")) {
            return "primevue";
          }
          if (id.includes("node_modules/vue") || id.includes("node_modules/vue-router")) {
            return "vue";
          }
          return undefined;
        },
      },
    },
  },
})
