import '@testing-library/jest-dom/vitest';

// jsdom does not implement matchMedia; Fluent UI queries it during render.
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList;
}

// jsdom does not implement ResizeObserver; Fluent UI's Drawer/Popover
// components construct one on mount even when they are closed (Sprint 16.1 —
// CSA wizard tests trip this because they render the wizard which mounts a
// CopilotDrawer with `open={false}`). Provide a no-op polyfill.
if (typeof window !== 'undefined' && !window.ResizeObserver) {
  class NoopResizeObserver {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  }
  window.ResizeObserver = NoopResizeObserver as unknown as typeof ResizeObserver;
}
