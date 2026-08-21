import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/tests/setup.ts",
    include: ["src/tests/**/*.test.tsx", "src/tests/**/*.test.ts"],

    coverage: {
      provider: "v8",
      reporter: ["text"],
    },
  },
});
