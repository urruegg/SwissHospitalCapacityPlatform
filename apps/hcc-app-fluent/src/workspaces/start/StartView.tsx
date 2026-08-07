import { useTranslation } from 'react-i18next';
import { makeStyles, tokens } from '@fluentui/react-components';
import { SectionHeader, type SectionTitlePart } from '../shared/narrative/SectionHeader';
import { NarrativeShell, type NarrativeSection } from '../shared/narrative/NarrativeShell';
import { ChallengerSection } from './frontier/ChallengerSection';
import { HospitalsSection } from './frontier/HospitalsSection';
import { NinetyDaySection } from './frontier/NinetyDaySection';
import { PatientPathLauncher } from './frontier/PatientPathLauncher';
import { StartHero } from './frontier/StartHero';
import { WhyCuraviasSection } from './frontier/WhyCuraviasSection';
import { WorkChartSection } from './frontier/WorkChartSection';
import { START_SECTIONS, type StartSection } from './frontier/start-content';

// Per-section eyebrow kicker + nav label — both i18n keys, localized en/de/fr/it
// (matches the Backstage nav-localization pattern in BackstageView.tsx).
const SECTION_META: Record<
  StartSection['id'],
  { eyebrowKey: string; navKey: string; accentKey?: string }
> = {
  hero: { eyebrowKey: '', navKey: 'start.frontier.nav.value' },
  challenger: {
    eyebrowKey: 'start.frontier.challenger.eyebrow',
    navKey: 'start.frontier.nav.challenger',
    accentKey: 'start.frontier.challenger.accent',
  },
  vision: {
    eyebrowKey: 'start.frontier.vision.eyebrow',
    navKey: 'start.frontier.nav.vision',
    accentKey: 'start.frontier.vision.accent',
  },
  'work-chart': {
    eyebrowKey: 'start.frontier.workChart.eyebrow',
    navKey: 'start.frontier.nav.operatingModel',
    accentKey: 'start.frontier.workChart.accent',
  },
  hospitals: {
    eyebrowKey: 'start.frontier.hospitals.eyebrow',
    navKey: 'start.frontier.nav.hospitals',
    accentKey: 'start.frontier.hospitals.accent',
  },
  'patient-path': {
    eyebrowKey: 'start.frontier.patientPath.eyebrow',
    navKey: 'start.frontier.nav.carePath',
    accentKey: 'start.frontier.patientPath.accent',
  },
  'ninety-day': {
    eyebrowKey: 'start.frontier.ninetyDay.eyebrow',
    navKey: 'start.frontier.nav.ninetyDay',
  },
};

const useStyles = makeStyles({
  sectionStack: {
    display: 'flex',
    flexDirection: 'column',
    rowGap: tokens.spacingVerticalXXL,
  },
});

function bodyKeyFor(section: StartSection) {
  return section.titleKey.replace(/\.title$/, '.body');
}

function toTitleParts(title: string, accent?: string): SectionTitlePart[] | undefined {
  if (!accent || !title.includes(accent)) return undefined;
  const i = title.indexOf(accent);
  return [
    { text: title.slice(0, i) },
    { text: accent, tone: 'accent' as const },
    { text: title.slice(i + accent.length) },
  ].filter((part) => part.text.length > 0);
}

function sectionBody(id: StartSection['id']) {
  switch (id) {
    case 'hero':
      return <StartHero />;
    case 'challenger':
      return <ChallengerSection />;
    case 'vision':
      return <WhyCuraviasSection />;
    case 'work-chart':
      // Sprint 40 — "Model": the org->work-chart block + Frontier Firm principle table.
      return <WorkChartSection />;
    case 'hospitals':
      // Sprint 40 — "Organisation": the three Swiss hospital archetypes + agent roster.
      return <HospitalsSection />;
    case 'patient-path':
      return <PatientPathLauncher />;
    case 'ninety-day':
      return <NinetyDaySection />;
  }
}

/**
 * Sprint 37 Start content presented through the shared narrative shell (P13-P17):
 * sticky section nav + one-per-screen storytelling + eyebrow headers, matching the
 * Backstage surface. Per Sprint 40 the intro preamble + guardrail chrome are dropped
 * so the surface opens directly on the hero (mockup fidelity); the advisory / synthetic /
 * no-PHI framing is carried by the hero trust pills + disclaimer.
 */
export function StartView() {
  const { t } = useTranslation();
  const styles = useStyles();

  const sections: NarrativeSection[] = START_SECTIONS.map((section) => {
    const meta = SECTION_META[section.id];
    const title = t(section.titleKey);
    const accent = meta.accentKey ? t(meta.accentKey) : undefined;
    const titleParts = toTitleParts(title, accent);

    return {
      key: section.id,
      label: t(meta.navKey),
      render: () => (
        <section
          data-start-section={section.id}
          data-testid={`start-${section.id}`}
          className={styles.sectionStack}
        >
          {section.id === 'hero' ? (
            sectionBody('hero')
          ) : (
            <>
              <SectionHeader
                id={section.id}
                variant="eyebrow"
                tagline={t(meta.eyebrowKey)}
                {...(titleParts ? { titleParts } : { header: title })}
                description={t(bodyKeyFor(section))}
              />
              {sectionBody(section.id)}
            </>
          )}
        </section>
      ),
    };
  });

  return (
    <div data-testid="start-view">
      <NarrativeShell
        sections={sections}
        navLabel={t('start.frontier.nav.label', 'Start sections')}
        navTestIdPrefix="start-nav"
        leadingGroupCount={1}
      />
    </div>
  );
}
