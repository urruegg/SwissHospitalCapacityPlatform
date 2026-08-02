import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import { RoleProvider } from '../../context/role-context';
import { AccountDialog } from './AccountDialog';
import { parseClaims } from '../../auth/claim-parser';

function renderAccount() {
  const claims = parseClaims({
    roles: ['HCC.PlatformAdmin', 'HCC.DischargeCoordinator'],
    oid: '7b9830a6-989b-4edd-b720-0d4bff7ffb2e',
    name: 'Admin User',
  });
  return render(
    <FluentProvider theme={webLightTheme}>
      <RoleProvider claims={claims}>
        <AccountDialog open onClose={() => {}} />
      </RoleProvider>
    </FluentProvider>,
  );
}

describe('AccountDialog (Sprint A, FR-AUTH-003)', () => {
  it('shows the held roles and the oid', () => {
    renderAccount();
    // PlatformAdmin is the highest held role, so it appears twice: as a held-role
    // badge and again in the "Active role" row of the lens. Both role labels must
    // render as badges; the oid must appear verbatim.
    expect(screen.getAllByText('HCC.PlatformAdmin').length).toBeGreaterThan(0);
    expect(screen.getByText('HCC.DischargeCoordinator')).toBeInTheDocument();
    expect(screen.getByText(/7b9830a6-989b-4edd-b720-0d4bff7ffb2e/)).toBeInTheDocument();
  });
});
