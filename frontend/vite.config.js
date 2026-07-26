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
      deps: {
        optimizer: {
          client: {
            enabled: true,
            // Include all MUI icons in the test bundle to prevent Vitest from loading
            // them individually, which significantly slows down unit test collection.
            include: ["@mui/icons-material"],
            rolldownOptions: {
              plugins: [
                {
                  // This plugin rewrites 'jsx-runtime' imports.
                  // A bug in React <= 17 prevents 'jsx-runtime' from resolving correctly
                  // in bundles built by Vitest. See https://github.com/facebook/react/issues/20235.
                  name: "fix-jsx-runtime",
                  resolveId(source) {
                    if (/jsx-runtime$/.test(source)) {
                      return path.resolve(__dirname, "node_modules", `${source}.js`)
                    }
                    return null
                  },
                },
              ],
            },
          }
        }
      }
    }
  };
});
