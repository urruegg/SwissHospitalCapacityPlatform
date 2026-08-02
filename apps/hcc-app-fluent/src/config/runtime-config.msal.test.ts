import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  getMsalClientId,
  getMsalTenantId,
  getMsalRedirectUri,
  getAppEnv,
  getHomeHospital,
} from './runtime-config';

describe('runtime MSAL config resolution', () => {
  afterEach(() => {
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
    vi.unstubAllEnvs();
  });

  it('prefers window.__ENV__ over the build-time VITE fallback', () => {
    // Competing build-time value: runtime must still win over VITE, not just the default.
    vi.stubEnv('VITE_MSAL_CLIENT_ID', 'build-time-should-lose');
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = {
      MSAL_CLIENT_ID: '52681a08-c792-44b1-b6b5-01cb560d450f',
      MSAL_TENANT_ID: '1337187a-4c41-4da9-8fca-731bba7a4329',
      MSAL_REDIRECT_URI: 'https://appsit.curavias.ch',
      APP_ENV: 'sit',
    };
    expect(getMsalClientId()).toBe('52681a08-c792-44b1-b6b5-01cb560d450f');
    expect(getMsalTenantId()).toBe('1337187a-4c41-4da9-8fca-731bba7a4329');
    expect(getMsalRedirectUri()).toBe('https://appsit.curavias.ch');
    expect(getAppEnv()).toBe('sit');
  });

  it('falls back to empty client id when nothing is configured (demo)', () => {
    expect(getMsalClientId()).toBe('');
  });

  it('resolves redirect uri to window.origin when neither runtime nor VITE is set', () => {
    expect(getMsalRedirectUri()).toBe(window.location.origin);
  });

  it('resolves redirect uri to the VITE fallback when no window.__ENV__', () => {
    vi.stubEnv('VITE_MSAL_REDIRECT_URI', 'https://build-time.curavias.ch');
    expect(getMsalRedirectUri()).toBe('https://build-time.curavias.ch');
  });

  it('resolves home hospital: runtime APP_HOME_HOSPITAL wins, else empty', () => {
    expect(getHomeHospital()).toBe('');
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = {
      APP_HOME_HOSPITAL: 'usz',
    };
    expect(getHomeHospital()).toBe('usz');
  });
});
