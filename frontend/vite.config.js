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
        ws: true, // Allow WebSocket upgrade for any /api/* path
        // IMPORTANT: Do NOT rewrite; backend expects /api prefix (FastAPI includes router with prefix "/api")
      },
      
      // 2. WebSocket Proxy: Handles the simulation endpoint. 
      // The frontend must connect to ws://localhost:5173/api/ws/simulate 
      // This prefix '/api/ws' correctly targets the FastAPI server.
      '/api/ws': {
        target: 'ws://localhost:8000', 
        ws: true, // IMPORTANT: Enables WebSocket proxying
        changeOrigin: true,
      },
    },
  },
});