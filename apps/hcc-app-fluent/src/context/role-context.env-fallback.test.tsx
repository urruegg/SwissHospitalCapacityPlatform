import { afterEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { canSwitchRole, RoleProvider, useRoleLens } from './role-context';
import { parseClaims } from '../auth/claim-parser';

describe('role lens env fallback (Sprint A)', () => {
  afterEach(() => {
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
  });

  it('enables the role switcher when APP_ENV=sit even if the token omits the env claim', () => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = { APP_ENV: 'sit' };
    // Token with roles but no `env` claim -> parseClaims defaults env to 'dev'.
    const claims = parseClaims({ roles: ['HCC.PlatformAdmin'] });
    expect(claims.env).toBe('dev');
    expect(canSwitchRole(claims)).toBe(true);
  });

  it('keeps the switcher hidden without a PlatformAdmin/DemoOperator role', () => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = { APP_ENV: 'sit' };
    const claims = parseClaims({ roles: ['HCC.DischargeCoordinator'] });
    expect(canSwitchRole(claims)).toBe(false);
  });
});

/** In-test probe: surfaces the derived hospital scope from the role lens. */
function ScopeProbe() {
  const { capabilities } = useRoleLens();
  return <span data-testid="scope">{capabilities.hospitalScope}</span>;
}

describe('role lens home-site runtime fallback (Sprint A)', () => {
  afterEach(() => {
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
  });

  it('resolves own-site scope to a valid runtime home when the hospital claim is absent', () => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = { APP_HOME_HOSPITAL: 'luks' };
    // No `hospital` claim -> parseClaims defaults to 'aggregated'; runtime home wins.
    const claims = parseClaims({ roles: ['HCC.DischargeCoordinator'] });
    render(
      <RoleProvider claims={claims}>
        <ScopeProbe />
      </RoleProvider>,
    );
    expect(screen.getByTestId('scope').textContent).toBe('luks');
  });

  it('falls back to the claim hospital when the runtime home is not a valid scope', () => {
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = { APP_HOME_HOSPITAL: 'atlantis' };
    // Invalid runtime home is rejected -> own-site resolves to the claim default 'aggregated'.
    const claims = parseClaims({ roles: ['HCC.DischargeCoordinator'] });
    render(
      <RoleProvider claims={claims}>
        <ScopeProbe />
      </RoleProvider>,
    );
    expect(screen.getByTestId('scope').textContent).toBe('aggregated');
  });
});
