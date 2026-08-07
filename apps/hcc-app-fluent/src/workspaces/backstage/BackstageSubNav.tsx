import { TabList, Tab } from '@fluentui/react-components';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

/**
 * Sprint 35 — Backstage sub-navigation.
 *
 * Mirrors the Main sub-nav pattern (Fluent `TabList` keyed by the `:widget`
 * route param). The Backstage surface now opens on the Digital Feedback Loop;
 * additional parts are added here as they land ("more to come").
 */
export const BACKSTAGE_PARTS = [
  { key: 'bva', labelKey: 'backstage.nav.bva' },
  { key: 'success-framework', labelKey: 'backstage.nav.successFramework' },
  { key: 'feedback-loop', labelKey: 'backstage.nav.feedbackLoop' },
  { key: 'solution-design', labelKey: 'backstage.nav.solutionDesign' },
  { key: 'devsecops-loop', labelKey: 'backstage.nav.devsecops' },
  { key: 'review-sessions', labelKey: 'backstage.nav.reviews' },
  { key: 'po-classes', labelKey: 'backstage.nav.poClasses' },
  { key: 'ninety-day', labelKey: 'backstage.nav.ninetyDay' },
] as const;

export const DEFAULT_BACKSTAGE_PART = BACKSTAGE_PARTS[0].key;

export function BackstageSubNav() {
  const nav = useNavigate();
  const { t } = useTranslation();
  const { widget = DEFAULT_BACKSTAGE_PART } = useParams();
  const selected = BACKSTAGE_PARTS.some((p) => p.key === widget) ? widget : DEFAULT_BACKSTAGE_PART;

  return (
    <TabList
      selectedValue={selected}
      aria-label={t('backstage.nav.label', 'Backstage sections')}
      onTabSelect={(_e, d) => {
        const part = BACKSTAGE_PARTS.find((p) => p.key === d.value);
        if (part) nav(`/backstage/${part.key}`);
      }}
    >
      {BACKSTAGE_PARTS.map((p) => (
        <Tab key={p.key} value={p.key} data-testid={`backstage-nav-${p.key}`}>
          {t(p.labelKey)}
        </Tab>
      ))}
    </TabList>
  );
}
