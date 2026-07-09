import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '../../src/i18n';
import { App } from '../../src/App';

describe('App shell', () => {
  it('renders the top bar brand and the app rail', () => {
    render(<App />);
    // Two brand occurrences (top bar title + home body); assert at least one.
    expect(screen.getAllByText(/Helvion/i).length).toBeGreaterThan(0);
    // DE default: the rail exposes Home ("Start") and Backstage tabs.
    expect(screen.getAllByText('Start').length).toBeGreaterThan(0);
    expect(screen.getByRole('tab', { name: 'Backstage' })).toBeInTheDocument();
  });

  it('hides the role switcher for an anonymous session', () => {
    render(<App />);
    expect(screen.queryByLabelText('Rolle wechseln')).toBeNull();
  });

  it('shows the role switcher for a SIT PlatformAdmin', () => {
    render(<App rawClaims={{ roles: ['HCC.PlatformAdmin'], env: 'sit', hospital: 'usz' }} />);
    expect(screen.getByLabelText('Rolle wechseln')).toBeInTheDocument();
  });
});
