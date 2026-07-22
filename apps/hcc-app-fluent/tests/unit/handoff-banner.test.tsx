import { beforeAll, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import i18n from '../../src/i18n';
import { HandoffBanner } from '../../src/shell/HandoffBanner';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('HandoffBanner', () => {
  it('renders the situation and a loop-back note when active', () => {
    render(
      <HandoffBanner
        banner={{ situation: 'Carried from ooa-agent: site -16 beds', loopBackToOoa: true }}
        provenance="simulated"
      />,
    );

    expect(screen.getByText(/site -16 beds/)).toBeInTheDocument();
    expect(screen.getByTestId('loop-back')).toBeInTheDocument();
    expect(screen.getByText(/simulated/i)).toBeInTheDocument();
  });

  it('omits the loop-back note when inactive and badges live context', () => {
    render(
      <HandoffBanner
        banner={{ situation: 'Current capacity context', loopBackToOoa: false }}
        provenance="live"
      />,
    );

    expect(screen.queryByTestId('loop-back')).not.toBeInTheDocument();
    expect(screen.getByText(/live/i)).toBeInTheDocument();
  });
});
