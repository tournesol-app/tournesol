import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(() => {
  return {
    resolve: {
      alias: {
        'src': path.resolve(__dirname, './src'),
      },
    },
    envPrefix: "REACT_APP_",
    build: {
      outDir: 'build',
      target: "es2015",
      rollupOptions: {
        output: {
          manualChunks: {
            // React hooks are bundled in a separate bundle to solve warnings
            // about circular dependencies with the default Vite config.
            "hooks": ["src/hooks"]
          }
        }
      }
    },
    plugins: [react()],
    server: {
      host: true,
      port: 3000
    },
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: 'src/setupTests.ts',
      clearMocks: true,
    }
  };
});
