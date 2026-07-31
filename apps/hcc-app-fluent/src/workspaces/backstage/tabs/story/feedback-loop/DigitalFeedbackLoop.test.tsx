import { fireEvent, render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { describe, expect, it, vi } from 'vitest';
import { DigitalFeedbackLoop } from './DigitalFeedbackLoop';
import { FEEDBACK_LOOP_DOMAINS } from './feedback-loop-model';

const renderLoop = (onDomainSelect = vi.fn()) => {
  render(
    <FluentProvider theme={webLightTheme}>
      <DigitalFeedbackLoop
        domains={FEEDBACK_LOOP_DOMAINS}
        onDomainSelect={onDomainSelect}
      />
    </FluentProvider>,
  );
  return onDomainSelect;
};

describe('DigitalFeedbackLoop', () => {
  it('selects a domain and emits it once', () => {
    const onSelect = renderLoop();
    const button = screen.getByRole('button', { name: /empower care teams/i });
    fireEvent.click(button);
    expect(button).toHaveAttribute('aria-pressed', 'true');
    expect(onSelect).toHaveBeenCalledOnce();
    expect(onSelect.mock.calls[0][0].id).toBe('frontier-workforce');
  });
});
