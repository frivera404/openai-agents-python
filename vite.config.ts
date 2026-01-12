import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

export default defineConfig(() => {
    return {
        plugins: [react()],
        server: {
            proxy: {
                '/api': {
                    // Proxy API calls to the backend. Use `VITE_API_BASE_URL` if set,
                    // otherwise default to the local Express backend on port 3002.
                    target: process.env.VITE_API_BASE_URL || 'http://127.0.0.1:3002',
                    changeOrigin: true,
                },
            },
        },
        // The `define` block has been removed to prevent exposing the API key to the client.
        // API calls are now proxied to a secure backend server.
        resolve: {
            alias: {
                '@': path.resolve(__dirname, '.'),
            },
        },
        build: {
            outDir: 'dev-ui',
            rollupOptions: {
                output: {
                    entryFileNames: 'main-PKDNKWJE.js',
                    chunkFileNames: '[name]-PKDNKWJE.js',
                    assetFileNames: '[name]-PKDNKWJE.[ext]',
                },
            },
        },
    };
});
