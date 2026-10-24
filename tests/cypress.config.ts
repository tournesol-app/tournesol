import { defineConfig } from 'cypress'
import plugins from "./cypress/plugins";

export default defineConfig({
  video: false,
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return plugins(on, config)
    },
    baseUrl: 'http://localhost:3000',
  },
  viewportWidth: 1920,
  viewportHeight: 1080,
});
