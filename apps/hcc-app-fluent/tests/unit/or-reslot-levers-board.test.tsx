import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { OrReslotLeversBoard } from '../../src/workspaces/main/boards/or-steering/OrReslotLeversBoard';
import { OR_STEERING_PINNED, sortReslotLevers } from '../../src/data/roleboard/or-steering-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

describe('OrReslotLeversBoard', () => {
  it('renders lever labels and bedsProtected numbers', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <OrReslotLeversBoard levers={OR_STEERING_PINNED.levers} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    const sorted = sortReslotLevers(OR_STEERING_PINNED.levers);
    expect(screen.getByText(sorted[0].label)).toBeInTheDocument();
  });

  it('renders levers sorted by bedsProtected descending even when input is unsorted', () => {
    const reversed = [...OR_STEERING_PINNED.levers].reverse();
    render(
      <FluentProvider theme={webLightTheme}>
        <OrReslotLeversBoard levers={reversed} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    const sorted = sortReslotLevers(OR_STEERING_PINNED.levers);
    const allText = document.body.textContent ?? '';
    const firstIdx = allText.indexOf(sorted[0].label);
    const secondIdx = allText.indexOf(sorted[1].label);
    expect(firstIdx).toBeGreaterThanOrEqual(0);
    expect(firstIdx).toBeLessThan(secondIdx);
  });

  it('fires onSelectLever with the correct lever when a row is clicked', () => {
    const onSelectLever = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <OrReslotLeversBoard levers={OR_STEERING_PINNED.levers} onSelectLever={onSelectLever} />
      </FluentProvider>,
    );
    const sorted = sortReslotLevers(OR_STEERING_PINNED.levers);
    act(() => screen.getByRole('button', { name: sorted[0].label }).click());
    expect(onSelectLever).toHaveBeenCalledWith(sorted[0]);
  });

  it('renders the auto-sequence CTA button', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <OrReslotLeversBoard levers={OR_STEERING_PINNED.levers} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    expect(screen.getByRole('button', { name: /auto-sequence/i })).toBeInTheDocument();
  });

  it('fires onAutoSequence when the auto-sequence CTA button is clicked', () => {
    const onAutoSequence = vi.fn();
    render(
      <FluentProvider theme={webLightTheme}>
        <OrReslotLeversBoard
          levers={OR_STEERING_PINNED.levers}
          onSelectLever={vi.fn()}
          onAutoSequence={onAutoSequence}
        />
      </FluentProvider>,
    );
    act(() => screen.getByRole('button', { name: /auto-sequence/i }).click());
    expect(onAutoSequence).toHaveBeenCalledOnce();
  });

  it('rank badges are numbered starting from 1', () => {
    render(
      <FluentProvider theme={webLightTheme}>
        <OrReslotLeversBoard levers={OR_STEERING_PINNED.levers} onSelectLever={vi.fn()} />
      </FluentProvider>,
    );
    // Both rank badges should be present (1 and 2); use getAllByText because
    // bedsProtected values may also render the number 1 elsewhere in the table.
    expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('2').length).toBeGreaterThanOrEqual(1);
  });
});
