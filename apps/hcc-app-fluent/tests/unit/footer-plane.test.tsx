import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FooterPlane } from '../../src/shell/planes/FooterPlane';

describe('FooterPlane', () => {
  it('shows the app version and a refresh-rate selector', () => {
    render(<FooterPlane />);
    expect(screen.getByText(/v\d+\.\d+\.\d+/)).toBeInTheDocument();
    expect(screen.getByLabelText(/refresh rate/i)).toBeInTheDocument();
  });
});
