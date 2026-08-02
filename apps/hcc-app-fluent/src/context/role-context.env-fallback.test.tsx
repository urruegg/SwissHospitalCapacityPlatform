import { afterEach, describe, expect, it } from 'vitest';
import { canSwitchRole } from './role-context';
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
