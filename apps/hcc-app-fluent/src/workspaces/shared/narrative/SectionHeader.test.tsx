import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it } from 'vitest';
import { SectionHeader } from './SectionHeader';

function renderHeader(ui: React.ReactElement) {
  return render(<FluentProvider theme={webLightTheme}>{ui}</FluentProvider>);
}

describe('SectionHeader titleParts', () => {
  it('renders one heading whose accessible name concatenates all parts', () => {
    renderHeader(
      <SectionHeader
        id="demo"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        titleParts={[
          { text: 'Here is what it looks like ' },
          { text: 'solved.', tone: 'accent' },
        ]}
      />,
    );
    const heading = screen.getByRole('heading', {
      name: /Here is what it looks like\s*solved\./i,
    });
    expect(heading.tagName).toBe('H2');
  });

  it('marks the accent part with the accent class and no aria-hidden', () => {
    renderHeader(
      <SectionHeader
        id="demo2"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        titleParts={[
          { text: 'From the org chart to the ' },
          { text: 'work chart', tone: 'accent' },
        ]}
      />,
    );
    const accent = screen.getByText('work chart');
    expect(accent.getAttribute('aria-hidden')).toBeNull();
    expect(accent.getAttribute('data-tone')).toBe('accent');
  });

  it('falls back to the header string when titleParts is omitted', () => {
    renderHeader(
      <SectionHeader
        id="demo3"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        header="Plain heading"
      />,
    );
    expect(screen.getByRole('heading', { name: 'Plain heading' })).toBeInTheDocument();
  });

  it('honours headingLevel=1', () => {
    renderHeader(
      <SectionHeader
        id="demo4"
        variant="eyebrow"
        tagline="Start"
        description="Lead copy."
        headingLevel={1}
        titleParts={[{ text: 'Top-level' }]}
      />,
    );
    expect(screen.getByRole('heading', { level: 1, name: 'Top-level' })).toBeInTheDocument();
  });
});
