import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen } from '@testing-library/react';
import i18n from '../../src/i18n';
import { App } from '../../src/App';

// Sprint 20 M6 — assert the language-independent English labels deterministically.
beforeAll(async () => {
  await i18n.changeLanguage('en');
});

/**
 * Sprint 20 M4 — App-level smoke for the routed five-plane shell.
 *
 * The legacy AppRail/TopBar assertions were superseded by the M4 RouterProvider
 * cutover; plane-level coverage lives in app-shell.test.tsx and
 * navigation-plane.test.tsx. This file proves <App/> wires the provider stack
 * (theme + role + hospital + browser router) and boots into the Start surface.
 */
describe('App (routed five-plane shell)', () => {
  it('boots into the five-plane shell with the Start surface as default route', () => {
    render(<App />);
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Primary' })).toBeInTheDocument();
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
  });

  it('exposes the four top-level navigation destinations', () => {
    render(<App />);
    ['Start', 'Main', 'Backstage', 'Settings'].forEach((n) =>
      expect(screen.getByRole('tab', { name: n })).toBeInTheDocument(),
    );
    expect(screen.queryByRole('tab', { name: 'CSA' })).not.toBeInTheDocument();
  });

  it('renders the header brand mark and role lens for a SIT PlatformAdmin', () => {
    render(<App rawClaims={{ roles: ['HCC.PlatformAdmin'], env: 'sit', hospital: 'usz' }} />);
    expect(screen.getAllByText('Curavias').length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Role')).toBeInTheDocument();
  });
});
