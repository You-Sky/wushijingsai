import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({ base: './', plugins: [react()], build: { rollupOptions: { output: { manualChunks(id) { const match = id.match(/section-(\d)\.json$/); return match ? `question-bank-${match[1]}` : undefined; } } } } });
