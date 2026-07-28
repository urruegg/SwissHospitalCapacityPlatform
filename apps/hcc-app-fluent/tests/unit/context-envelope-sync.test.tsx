import { afterEach, describe, expect, it } from 'vitest';
import { render } from '@testing-library/react';
import { RoleProvider } from '../../src/context/role-context';
import { DataSourceProvider } from '../../src/context/data-source-context';
import { ContextEnvelopeSync } from '../../src/context/context-envelope-sync';
import {
  getContextEnvelope,
  setContextEnvelope,
} from '../../src/data/roleboard/golden-source-client';
import { parseClaims } from '../../src/auth/claim-parser';

afterEach(() => setContextEnvelope(null));

describe('ContextEnvelopeSync (shell read-path envelope)', () => {
  it('publishes a ContextEnvelope derived from the active role lens', () => {
    const claims = parseClaims({
      roles: ['HCC.BedManager'],
      hospital: 'usz',
      env: 'sit',
      oid: 'oid-1',
    });

    render(
      <RoleProvider claims={claims}>
        <DataSourceProvider>
          <ContextEnvelopeSync />
        </DataSourceProvider>
      </RoleProvider>,
    );

    const env = getContextEnvelope();
    expect(env).not.toBeNull();
    expect(env?.userOid).toBe('oid-1');
    expect(env?.activeRole).toBe('HCC.BedManager');
    // Shell envelope is board-agnostic; boards pass hospital/window explicitly.
    expect(env?.agent).toBeNull();
    expect(env?.windowHours).toBe(72);
    // Default toggle is simulated until a golden source is configured.
    expect(env?.dataSource).toBe('simulated');
  });

  it('falls back to a least-privilege envelope for the anonymous demo guest', () => {
    const claims = parseClaims(undefined);

    render(
      <RoleProvider claims={claims}>
        <DataSourceProvider>
          <ContextEnvelopeSync />
        </DataSourceProvider>
      </RoleProvider>,
    );

    const env = getContextEnvelope();
    expect(env).not.toBeNull();
    expect(env?.userOid).toBeNull();
    expect(env?.activeRole).toBe('HCC.Viewer');
    expect(env?.hospitalScope).toBe('aggregated');
  });
});
