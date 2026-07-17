import '../../src/i18n';
import { render, screen, within } from '@testing-library/react';
import { HeaderPlane } from '../../src/shell/planes/HeaderPlane';
import { RoleProvider } from '../../src/context/role-context';
import { ThemeModeProvider } from '../../src/theme/theme-context';

function renderHeader(roles: string[]) {
  return render(
    <ThemeModeProvider>
      <RoleProvider testRoles={roles} testHomeSite="usz">
        <HeaderPlane />
      </RoleProvider>
    </ThemeModeProvider>,
  );
}

describe('HeaderPlane', () => {
  it('shows the brand on the left and all five right-aligned controls', () => {
    renderHeader(['HCC.PlatformAdmin', 'HCC.Viewer']);
    const header = screen.getByRole('banner');
    expect(within(header).getByText('Curavias')).toBeInTheDocument();
    expect(within(header).getByLabelText(/theme/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/language/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/hospital/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/role/i)).toBeInTheDocument();
    expect(within(header).getByLabelText(/user/i)).toBeInTheDocument();
  });

  it('the role dropdown lists only held roles', () => {
    renderHeader(['HCC.PlatformAdmin', 'HCC.Viewer']);
    const role = screen.getByLabelText(/role/i);
    expect(within(role).queryByText('HCC.BedManager')).not.toBeInTheDocument();
  });
});
