import { afterEach, describe, expect, it } from 'vitest';
import { getMsalClientId, getMsalTenantId, getMsalRedirectUri, getAppEnv } from './runtime-config';

describe('runtime MSAL config resolution', () => {
  afterEach(() => {
    delete (window as unknown as { __ENV__?: unknown }).__ENV__;
  });

  it('prefers window.__ENV__ over build-time fallback', () => {
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
});
