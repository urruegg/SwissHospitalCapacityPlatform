import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { NARROW_VIEWPORT_HEIGHT, NARROW_VIEWPORT_WIDTH } from './responsive';

const START_SECTION_IDS = [
  'hero',
  'work-chart',
  'cio-why-now',
  'hospitals',
  'patient-path',
  'ninety-day',
  'bva',
] as const;

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
  });
  await page.goto('/start');
  await expect(page.getByTestId('start-view')).toBeVisible();
});

async function attachFullPageScreenshot(page: Page, testInfo: TestInfo, name: string) {
  const originalState = await page.evaluate(() => {
    const main = document.querySelector<HTMLElement>('main');
    const shell = main?.parentElement;

    const state = {
      mainStyle: main?.style.cssText ?? '',
      mainScrollTop: main?.scrollTop ?? 0,
      shellStyle: shell?.style.cssText ?? '',
    };

    if (main) {
      main.scrollTop = 0;
      main.style.overflow = 'visible';
      main.style.height = 'auto';
    }
    if (shell) {
      shell.style.height = 'auto';
      shell.style.minHeight = '100vh';
      shell.style.gridTemplateRows = 'auto auto auto';
    }

    return state;
  });

  const screenshotPath = testInfo.outputPath(`${name}.png`);
  try {
    await page.screenshot({
      path: screenshotPath,
      fullPage: true,
      animations: 'disabled',
    });
    await testInfo.attach(name, { path: screenshotPath, contentType: 'image/png' });
  } finally {
    await page.evaluate((state) => {
      const main = document.querySelector<HTMLElement>('main');
      const shell = main?.parentElement;

      if (main) {
        main.scrollTop = state.mainScrollTop;
        main.style.cssText = state.mainStyle;
      }
      if (shell) {
        shell.style.cssText = state.shellStyle;
      }
    }, originalState);
  }
}

async function readScreenshotTargetInlineStyles(page: Page) {
  return page.evaluate(() => {
    const main = document.querySelector<HTMLElement>('main');
    const shell = main?.parentElement;

    return {
      main: main?.style.cssText ?? '',
      shell: shell?.style.cssText ?? '',
    };
  });
}

test('restores shell inline styles after taking a full-page screenshot', async ({
  page,
}, testInfo) => {
  const stylesBefore = await readScreenshotTargetInlineStyles(page);

  await attachFullPageScreenshot(page, testInfo, 'start-style-restoration');

  await expect.poll(() => readScreenshotTargetInlineStyles(page)).toEqual(stylesBefore);
});

test('renders the seven approved Start sections in blueprint order without legacy placeholders', async ({
  page,
}, testInfo) => {
  const startSections = page.getByTestId('start-view').locator('[data-start-section]');
  await expect(startSections).toHaveCount(START_SECTION_IDS.length);
  const renderedIds = await startSections.evaluateAll((sections) =>
    sections.map((section) => section.getAttribute('data-start-section')),
  );

  expect(renderedIds).toEqual(START_SECTION_IDS);
  await expect(page.getByTestId('start-capacity-teaser')).toHaveCount(0);
  await expect(page.getByTestId('launch-occupancy')).toHaveCount(0);
  await expect(page.getByText(/placeholder|launcher section|coming soon/i)).toHaveCount(0);

  await attachFullPageScreenshot(page, testInfo, 'start-desktop-full-page');
});

test('patient-path links navigate into the real discharge and occupancy boards', async ({
  page,
}) => {
  await page.getByRole('link', { name: /open discharge role board/i }).click();
  await expect(page).toHaveURL(/\/main\/discharge$/);
  await expect(page.getByTestId('board-discharge')).toBeVisible();

  await page.goto('/start');
  await page.getByRole('link', { name: /open occupancy role board/i }).click();
  await expect(page).toHaveURL(/\/main\/occupancy$/);
  await expect(page.getByTestId('board-occupancy')).toBeVisible();
});

test('uses the existing shell agent rail for the Product Owner Agent', async ({ page }) => {
  await page.getByRole('button', { name: /open agent/i }).click();

  const rail = page.getByRole('complementary', { name: 'Agent' });
  await expect(rail).toBeVisible();
  await expect(rail).toContainText('product-owner-agent');
});

test('shows synthetic/no-PHI and advisory/human-decision guardrails', async ({ page }) => {
  await expect(page.getByText(/synthetic, generic, non-PHI content only/i).first()).toBeVisible();
  await expect(page.getByText(/Advisory only/i).first()).toBeVisible();
  await expect(page.getByText(/The human decides\./i).first()).toBeVisible();
});

test(`keeps every Start section reachable without document overflow at ${NARROW_VIEWPORT_WIDTH}x${NARROW_VIEWPORT_HEIGHT}`, async ({
  page,
}, testInfo) => {
  await page.setViewportSize({
    width: NARROW_VIEWPORT_WIDTH,
    height: NARROW_VIEWPORT_HEIGHT,
  });
  await page.reload();
  await expect(page.getByTestId('start-view')).toBeVisible();

  // Intentionally scan the full DOM only in this narrow diagnostic so failures name offenders.
  const documentOverflow = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const offenders = Array.from(document.querySelectorAll<HTMLElement>('body *'))
      .map((element) => {
        const rect = element.getBoundingClientRect();
        return {
          tag: element.tagName.toLowerCase(),
          testId: element.dataset.testid ?? '',
          className: element.getAttribute('class') ?? '',
          left: Math.round(rect.left),
          right: Math.round(rect.right),
          width: Math.round(rect.width),
        };
      })
      .filter(({ left, right }) => left < -1 || right > viewportWidth + 1)
      .sort((a, b) => b.right - a.right)
      .slice(0, 10);

    return {
      document: document.documentElement.scrollWidth - viewportWidth,
      body: document.body.scrollWidth - document.body.clientWidth,
      offenders,
    };
  });
  expect(
    documentOverflow.document,
    JSON.stringify(documentOverflow.offenders, null, 2),
  ).toBeLessThanOrEqual(0);
  expect(documentOverflow.body).toBeLessThanOrEqual(0);

  await page.getByRole('button', { name: /collapse navigation/i }).click();
  await expect(page.getByRole('button', { name: /expand navigation/i })).toBeVisible();

  for (const id of START_SECTION_IDS) {
    const section = page.getByTestId(`start-${id}`);
    await section.evaluate((element) => element.scrollIntoView({ block: 'start' }));
    await expect(section).toBeVisible();
    const position = await section.evaluate((element) => {
      const sectionRect = element.getBoundingClientRect();
      const mainRect = element.closest('main')?.getBoundingClientRect();
      return {
        top: sectionRect.top,
        bottom: sectionRect.bottom,
        width: sectionRect.width,
        mainTop: mainRect?.top ?? 0,
        mainBottom: mainRect?.bottom ?? window.innerHeight,
      };
    });
    expect(position.width, `${id} section must fit within the narrow viewport`).toBeLessThanOrEqual(
      NARROW_VIEWPORT_WIDTH,
    );
    expect(position.bottom, `${id} section must reach the visible main viewport`).toBeGreaterThan(
      position.mainTop,
    );
    expect(position.top, `${id} section must reach the visible main viewport`).toBeLessThan(
      position.mainBottom,
    );
  }

  await attachFullPageScreenshot(page, testInfo, 'start-narrow-full-page');
});
