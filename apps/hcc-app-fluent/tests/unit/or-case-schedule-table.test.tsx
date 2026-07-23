import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { OrCaseScheduleTable } from '../../src/workspaces/main/boards/or-steering/OrCaseScheduleTable';
import { OR_STEERING_PINNED } from '../../src/data/roleboard/or-steering-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('OrCaseScheduleTable', () => {
  it('renders all cases showing specialty and slot', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <OrCaseScheduleTable cases={OR_STEERING_PINNED.cases} onSelectCase={vi.fn()} />
      </FluentProvider>,
    );
    for (const c of OR_STEERING_PINNED.cases) {
      expect(screen.getByText(c.specialty)).toBeInTheDocument();
      expect(screen.getByText(c.slot)).toBeInTheDocument();
    }
  });

  it('renders Yes badge for deferable cases and No badge for non-deferable', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <OrCaseScheduleTable cases={OR_STEERING_PINNED.cases} onSelectCase={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.getAllByText('Yes')[0]).toBeInTheDocument();
    expect(screen.getByText('No')).toBeInTheDocument();
  });

  it('fires onSelectCase with the correct case when a row is clicked', () => {
    const onSelectCase = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <OrCaseScheduleTable cases={OR_STEERING_PINNED.cases} onSelectCase={onSelectCase} />
      </FluentProvider>,
    );
    const firstCase = OR_STEERING_PINNED.cases[0]; // ortho-knee-tue
    act(() =>
      screen.getByRole('button', { name: /Defer Orthopedics case/i }).click(),
    );
    expect(onSelectCase).toHaveBeenCalledWith(firstCase);
  });

  it('renders a row with role=button for every case', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <OrCaseScheduleTable cases={OR_STEERING_PINNED.cases} onSelectCase={vi.fn()} />
      </FluentProvider>,
    );
    // Each case row has role="button"; there may also be badge elements
    const rows = screen.getAllByRole('button');
    expect(rows.length).toBeGreaterThanOrEqual(OR_STEERING_PINNED.cases.length);
  });

  it('calls onSelectCase with the correct General surgery case when that row is clicked', () => {
    const onSelectCase = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <OrCaseScheduleTable cases={OR_STEERING_PINNED.cases} onSelectCase={onSelectCase} />
      </FluentProvider>,
    );
    const herniaCase = OR_STEERING_PINNED.cases.find((c) => c.id === 'gen-hernia-tue')!;
    act(() =>
      screen.getByRole('button', { name: /Defer General surgery case/i }).click(),
    );
    expect(onSelectCase).toHaveBeenCalledWith(herniaCase);
  });
});
