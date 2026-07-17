import { render, screen, act } from '@testing-library/react';
import { RoleProvider, useRoleLens } from '../../src/context/role-context';

function Probe() {
  const { activeRole, capabilities, setActiveRole } = useRoleLens();
  return (
    <div>
      <span data-testid="role">{activeRole}</span>
      <span data-testid="ceiling">{capabilities.agentCeiling}</span>
      <button onClick={() => setActiveRole('HCC.PlatformAdmin')}>elevate</button>
    </div>
  );
}

describe('role lens', () => {
  it('defaults to the highest held role and refuses to elevate beyond held roles', () => {
    render(
      <RoleProvider testRoles={['HCC.Viewer']} testHomeSite="usz">
        <Probe />
      </RoleProvider>,
    );
    expect(screen.getByTestId('role').textContent).toBe('HCC.Viewer');
    act(() => screen.getByText('elevate').click());
    expect(screen.getByTestId('role').textContent).toBe('HCC.Viewer'); // narrow-only
    expect(screen.getByTestId('ceiling').textContent).toBe('read');
  });

  it('defaults to the highest held role when several are held', () => {
    render(
      <RoleProvider testRoles={['HCC.Viewer', 'HCC.PlatformAdmin']} testHomeSite="usz">
        <Probe />
      </RoleProvider>,
    );
    expect(screen.getByTestId('role').textContent).toBe('HCC.PlatformAdmin');
    expect(screen.getByTestId('ceiling').textContent).toBe('deploy');
  });
});
