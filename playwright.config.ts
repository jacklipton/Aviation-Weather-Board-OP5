import { defineConfig, devices } from '@playwright/test';

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
// import dotenv from 'dotenv';
// import path from 'path';
// dotenv.config({ path: path.resolve(__dirname, '.env') });

const MOCK_PORT = 8081;
const MOCK_URL = `http://localhost:${MOCK_PORT}`;

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './e2e',
  /* Tests share one server + board state, so run them serially. */
  fullyParallel: false,
  workers: 1,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('')`.
       Default is a mock-mode server on :8081 started below (never the live
       hardware board on :8080). Set PLAYWRIGHT_BASE_URL to test a running
       instance instead. */
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? MOCK_URL,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
  },

  /* Run a mock-mode server (MockLightController, no SPI) for the tests. */
  webServer: process.env.PLAYWRIGHT_BASE_URL ? undefined : {
    command: `.venv/bin/python -m uvicorn src.web_app:app --host 127.0.0.1 --port ${MOCK_PORT}`,
    url: MOCK_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      ENVIRONMENT: 'local',
      HOST: '127.0.0.1',
      PORT: String(MOCK_PORT),
    },
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  /* Run your local dev server before starting the tests */
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
