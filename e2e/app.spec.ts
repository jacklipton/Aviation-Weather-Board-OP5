import { expect, test } from '@playwright/test';

/**
 * IMPORTANT: With the default config these tests run against a MOCK server
 * (MockLightController) on :8081 started by playwright.config.ts — the real
 * LED strip on :8080 is never touched. To test against a running instance
 * instead: PLAYWRIGHT_BASE_URL=http://localhost:8080 npm run e2e
 */

test.describe('Aviation Weather Board', () => {
  test('home page loads with title and heading', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/Aviation Weather Board/);
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/Aviation Weather/i);
  });

  test('header shows Start/Stop, Refresh and brightness controls', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('button', { name: /Start|Stop/i }).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /Refresh/i })).toBeVisible();
    await expect(page.locator('input[type="range"]')).toBeVisible();
  });

  test('status API responds', async ({ request }) => {
    const response = await request.get('/api/status');
    expect(response.ok()).toBeTruthy();

    const status = await response.json();
    expect(status).toHaveProperty('active');
    expect(status).toHaveProperty('uptime_seconds');
    expect(status).toHaveProperty('brightness');
    // uptime tracking is real now, not the old stubbed 0.0
    expect(status.uptime_seconds).toBeGreaterThanOrEqual(0);
  });

  test('stop sets status inactive and the UI reflects it', async ({ page, request }) => {
    // Ensure board reports stopped at the API level
    const stop = await request.post('/api/control/stop');
    expect(stop.ok()).toBeTruthy();

    await page.goto('/');
    // Status dot text flips to "System Stopped" (polled every 5s, wait for it)
    await expect(page.getByText(/System Stopped/i)).toBeVisible({ timeout: 10_000 });
    await expect(page.getByRole('button', { name: /Start/i })).toBeVisible();

    const status = await (await request.get('/api/status')).json();
    expect(status.active).toBeFalsy();
  });

  test('start restarts the board and status becomes active again', async ({ page, request }) => {
    // Put board into stopped state first
    await request.post('/api/control/stop');

    await page.goto('/');
    await page.getByRole('button', { name: /Start/i }).click();

    // UI should flip to active view (button becomes Stop)
    await expect(page.getByRole('button', { name: /Stop/i })).toBeVisible({ timeout: 10_000 });

    const status = await (await request.get('/api/status')).json();
    expect(status.active).toBeTruthy();
  });

  test('brightness can be set and read back from status', async ({ request }) => {
    const res = await request.post('/api/control/brightness', {
      data: { brightness: 128 },
    });
    expect(res.ok()).toBeTruthy();

    const status = await (await request.get('/api/status')).json();
    expect(status.brightness).toBe(128);

    // Restore a sane default
    await request.post('/api/control/brightness', { data: { brightness: 64 } });
  });

  test('brightness slider updates the value shown next to it', async ({ page }) => {
    await page.goto('/');

    const slider = page.locator('input[type="range"]');
    await slider.evaluate((el) => {
      // React overrides the value property, so use the native setter + input event
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!;
      setter.call(el, '200');
      el.dispatchEvent(new Event('input', { bubbles: true }));
    });

    await expect(page.getByTestId('brightness-value')).toHaveText('200', { timeout: 5_000 });
  });

  test('weather data loads for the configured airports', async ({ request }) => {
    test.skip(!process.env.CHECKWX_API_KEY, 'No CHECKWX_API_KEY; skipping live weather test');

    // Trigger an instant refresh and wait for cached data to appear
    await request.post('/api/control/refresh');

    const deadline = Date.now() + 30_000;
    let airports: any[] = [];
    while (Date.now() < deadline) {
      const res = await request.get('/api/weather');
      if (res.ok()) airports = await res.json();
      if (airports.length > 0) break;
      await new Promise((r) => setTimeout(r, 1500));
    }

    expect(airports.length).toBeGreaterThan(0);
    for (const a of airports.slice(0, 5)) {
      expect(a).toHaveProperty('icao');
      expect(a).toHaveProperty('flight_category');
    }
  });

  test('airport cards appear on the page with METAR data', async ({ page, request }) => {
    test.skip(!process.env.CHECKWX_API_KEY, 'No CHECKWX_API_KEY; skipping live weather test');

    await request.post('/api/control/refresh');
    const deadline = Date.now() + 30_000;
    let count = 0;
    while (Date.now() < deadline) {
      const res = await request.get('/api/weather');
      count = res.ok() ? (await res.json()).length : 0;
      if (count > 0) break;
      await new Promise((r) => setTimeout(r, 1500));
    }
    test.skip(count === 0, 'Weather API unavailable');

    await page.goto('/');
    // Each cached airport renders as a card; screenshot first card's ICAO code
    const firstCard = page.locator('main .grid > div').first();
    await expect(firstCard).toBeVisible({ timeout: 15_000 });
    // First card shows its ICAO code as a heading (e.g. "CYGK")
    await expect(firstCard.getByRole('heading', { level: 3 })).toHaveText(/^[A-Z]{4}$/);
  });
});
