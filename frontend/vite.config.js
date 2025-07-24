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
      deps: {
        optimizer: {
          web: {
            // Include all MUI icons in the test bundle to prevent Vitest from loading
            // them individually, which significantly slows down unit test collection.
            include: ["@mui/icons-material"],
            esbuildOptions: {
              plugins: [
                {
                  // This plugin rewrites 'jsx-runtime' imports.
                  // A bug in React <= 17 prevents 'jsx-runtime' from resolving correctly
                  // in bundles built by Vitest. See https://github.com/facebook/react/issues/20235.
                  name: "fix-jsx-runtime",
                  setup: (build) => {
                    build.onResolve({ filter: /jsx-runtime$/ }, args => {
                      return { path: path.resolve(__dirname, "node_modules", `${args.path}.js`) }
                    })
                  }
                }
              ]
            }
          }
        }
      }
    }
  };
});
