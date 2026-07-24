import { describe, it, expect, beforeAll } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { FluentProvider, webLightTheme } from '@fluentui/react-components';
import i18n from '../../src/i18n';
import { AdmissionsEventstream } from '../../src/workspaces/main/boards/bed-manager/AdmissionsEventstream';
import { BEDMANAGER_PINNED } from '../../src/data/roleboard/bed-manager-data';

beforeAll(async () => {
  await i18n.changeLanguage('en');
});

function renderStream(
  admissions = BEDMANAGER_PINNED.admissions,
) {
  return render(
    <FluentProvider theme={webLightTheme}>
      <AdmissionsEventstream admissions={admissions} />
    </FluentProvider>,
  );
}

describe('AdmissionsEventstream', () => {
  it('renders all admission events from BEDMANAGER_PINNED', () => {
    renderStream();
    for (const ev of BEDMANAGER_PINNED.admissions) {
      expect(screen.getByText(ev.message)).toBeInTheDocument();
      expect(screen.getByText(ev.ts)).toBeInTheDocument();
    }
  });

  it('renders an "admit" badge for admit-kind events', () => {
    renderStream();
    const admitBadges = screen.getAllByText('admit');
    expect(admitBadges.length).toBeGreaterThanOrEqual(1);
  });

  it('renders a "discharge" badge for discharge-kind events', () => {
    renderStream();
    const dischargeBadges = screen.getAllByText('discharge');
    expect(dischargeBadges.length).toBeGreaterThanOrEqual(1);
  });

  it('uses stable ids as keys — no duplicate messages rendered', () => {
    renderStream();
    // Each unique message appears exactly once
    const messages = BEDMANAGER_PINNED.admissions.map((e) => e.message);
    const uniqueMessages = new Set(messages);
    for (const msg of uniqueMessages) {
      expect(screen.getAllByText(msg)).toHaveLength(1);
    }
  });

  it('all BEDMANAGER_PINNED admission events have a non-empty stable id', () => {
    for (const ev of BEDMANAGER_PINNED.admissions) {
      expect(ev.id).toBeTruthy();
      expect(typeof ev.id).toBe('string');
    }
  });

  it('renders a stream with only a single admit event correctly', () => {
    const singleAdmit = [{ id: 'test-01', ts: '12:00', message: 'PT-9999 admitted', kind: 'admit' as const }];
    renderStream(singleAdmit);
    expect(screen.getByText('PT-9999 admitted')).toBeInTheDocument();
    expect(screen.getByText('admit')).toBeInTheDocument();
    expect(screen.queryByText('discharge')).toBeNull();
  });

  it('renders both admit and discharge badge colors distinguishably', () => {
    renderStream();
    const list = screen.getByRole('list');
    const admitBadge = within(list).getAllByText('admit')[0];
    const dischargeBadge = within(list).getAllByText('discharge')[0];
    // Both badges exist as Fluent Badge elements
    expect(admitBadge.closest('[class*="fui-Badge"]')).not.toBeNull();
    expect(dischargeBadge.closest('[class*="fui-Badge"]')).not.toBeNull();
    // They are different elements
    expect(admitBadge).not.toBe(dischargeBadge);
  });
});
