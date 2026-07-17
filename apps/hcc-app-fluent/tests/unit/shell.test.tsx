import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '../../src/i18n';
import { App } from '../../src/App';

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

  it('exposes all five navigation destinations (disabled-not-hidden gating)', () => {
    render(<App />);
    ['Start', 'Main', 'CSA', 'Backstage', 'Settings'].forEach((n) =>
      expect(screen.getByRole('tab', { name: n })).toBeInTheDocument(),
    );
  });

  it('renders the header brand mark and role lens for a SIT PlatformAdmin', () => {
    render(<App rawClaims={{ roles: ['HCC.PlatformAdmin'], env: 'sit', hospital: 'usz' }} />);
    expect(screen.getAllByText('Curavias').length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Role')).toBeInTheDocument();
  });
});
