import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { Hospital, ParsedClaims } from '../auth/claim-parser';

/**
 * Sprint 13 T2 — hospital context.
 *
 * Seeds the active hospital from the `hospital` claim and lets an authorised
 * operator switch the active hospital scope (the switcher visibility is gated by
 * the role context; this provider just holds the value).
 */
interface HospitalContextValue {
  hospital: Hospital;
  setHospital: (h: Hospital) => void;
  claimHospital: Hospital;
}

const HospitalContext = createContext<HospitalContextValue | undefined>(undefined);

export function HospitalProvider({
  claims,
  children,
}: {
  claims: ParsedClaims;
  children: ReactNode;
}) {
  const [hospital, setHospital] = useState<Hospital>(claims.hospital);
  const value = useMemo<HospitalContextValue>(
    () => ({ hospital, setHospital, claimHospital: claims.hospital }),
    [hospital, claims.hospital],
  );
  return <HospitalContext.Provider value={value}>{children}</HospitalContext.Provider>;
}

export function useHospital(): HospitalContextValue {
  const ctx = useContext(HospitalContext);
  if (!ctx) throw new Error('useHospital must be used within a HospitalProvider');
  return ctx;
}
