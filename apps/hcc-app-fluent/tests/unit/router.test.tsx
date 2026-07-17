import { render, screen } from '@testing-library/react';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { routes } from '../../src/shell/router';

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] });
  return render(<RouterProvider router={router} />);
}

describe('routes', () => {
  it('defaults "/" to the Start surface', () => {
    renderAt('/');
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
  });

  it('redirects unknown paths to Start', () => {
    renderAt('/nope');
    expect(screen.getByTestId('start-view')).toBeInTheDocument();
  });
});
