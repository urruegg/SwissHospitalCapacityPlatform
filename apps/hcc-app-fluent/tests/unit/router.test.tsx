import '../../src/i18n';
import { render, screen } from '@testing-library/react';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { routes } from '../../src/shell/router';
import { ThemeModeProvider } from '../../src/theme/theme-context';
import { RoleProvider } from '../../src/context/role-context';

function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] });
  return render(
    <ThemeModeProvider>
      <RoleProvider>
        <RouterProvider router={router} />
      </RoleProvider>
    </ThemeModeProvider>,
  );
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
