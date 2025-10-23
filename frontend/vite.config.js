import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // This is the standard React/Vite dev port
    proxy: {
      // 1. REST Proxy: Handles all API calls, removing the /api prefix before sending to FastAPI
      '/api': {
        target: 'http://localhost:8000', 
        changeOrigin: true,
        // The rewrite rule is CORRECT for REST endpoints like /api/graph/new
        rewrite: (path) => path.replace(/^\/api/, ''), 
      },
      
      // 2. WebSocket Proxy: Handles the simulation endpoint. 
      // The frontend must connect to ws://localhost:5173/api/ws/simulate 
      // This prefix '/api/ws' correctly targets the FastAPI server.
      '/api/ws': {
        target: 'ws://localhost:8000', 
        ws: true, // IMPORTANT: Enables WebSocket proxying
      },
    },
  },
});