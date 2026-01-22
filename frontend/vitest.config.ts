// File: frontend/vitest.config.ts
// Description: Vitest configuration for frontend tests
// Version: 1.0

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["src/**/*.test.{ts,tsx}"],
    exclude: ["node_modules", "dist"],
    reporters: ["verbose"],
    outputFile: undefined, // Disable file output, use console
  },
});
