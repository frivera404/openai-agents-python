import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(() => {
    return {
      plugins: [react()],
      server: {
        proxy: {
          '/api': {
            target: 'http://localhost:3001',
            changeOrigin: true,
          },
        },
      },
      // The `define` block has been removed to prevent exposing the API key to the client.
      // API calls are now proxied to a secure backend server.
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      },
      build: {
        outDir: 'dev-ui',
        rollupOptions: {
          output: {
            entryFileNames: 'main-PKDNKWJE.js',
            chunkFileNames: '[name]-PKDNKWJE.js',
            assetFileNames: '[name]-PKDNKWJE.[ext]'
          }
        }
      }
    };
});
