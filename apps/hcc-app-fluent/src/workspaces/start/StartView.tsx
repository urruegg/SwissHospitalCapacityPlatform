import { useTranslation } from 'react-i18next';
import { SectionHeader } from '../shared/narrative/SectionHeader';
import { NarrativeShell, type NarrativeSection } from '../shared/narrative/NarrativeShell';
import { BvaDecisionSection } from './frontier/BvaDecisionSection';
import { ChallengerSection } from './frontier/ChallengerSection';
import { CioChallengerSection } from './frontier/CioChallengerSection';
import { HospitalsSection } from './frontier/HospitalsSection';
import { NinetyDaySection } from './frontier/NinetyDaySection';
import { PatientPathLauncher } from './frontier/PatientPathLauncher';
import { StartHero } from './frontier/StartHero';
import { WhyCuraviasSection } from './frontier/WhyCuraviasSection';
import { WorkChartSection } from './frontier/WorkChartSection';
import { START_SECTIONS, type StartSection } from './frontier/start-content';

// Per-section eyebrow kicker + nav label — both i18n keys, localized en/de/fr/it
// (matches the Backstage nav-localization pattern in BackstageView.tsx).
const SECTION_META: Record<StartSection['id'], { eyebrowKey: string; navKey: string }> = {
  hero: { eyebrowKey: '', navKey: 'start.frontier.nav.value' },
  challenger: {
    eyebrowKey: 'start.frontier.challenger.eyebrow',
    navKey: 'start.frontier.nav.challenger',
  },
  vision: {
    eyebrowKey: 'start.frontier.vision.eyebrow',
    navKey: 'start.frontier.nav.vision',
  },
  'work-chart': {
    eyebrowKey: 'start.frontier.workChart.eyebrow',
    navKey: 'start.frontier.nav.operatingModel',
  },
  hospitals: {
    eyebrowKey: 'start.frontier.hospitals.eyebrow',
    navKey: 'start.frontier.nav.hospitals',
  },
  'cio-why-now': {
    eyebrowKey: 'start.frontier.cioWhyNow.eyebrow',
    navKey: 'start.frontier.nav.whyNow',
  },
  'patient-path': {
    eyebrowKey: 'start.frontier.patientPath.eyebrow',
    navKey: 'start.frontier.nav.carePath',
  },
  'ninety-day': {
    eyebrowKey: 'start.frontier.ninetyDay.eyebrow',
    navKey: 'start.frontier.nav.ninetyDay',
  },
  bva: { eyebrowKey: 'start.frontier.bva.eyebrow', navKey: 'start.frontier.nav.bva' },
};

function bodyKeyFor(section: StartSection) {
  return section.titleKey.replace(/\.title$/, '.body');
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
    case 'cio-why-now':
      return <CioChallengerSection />;
    case 'patient-path':
      return <PatientPathLauncher />;
    case 'ninety-day':
      return <NinetyDaySection />;
    case 'bva':
      return <BvaDecisionSection />;
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

  const sections: NarrativeSection[] = START_SECTIONS.map((section) => ({
    key: section.id,
    label: t(SECTION_META[section.id].navKey),
    render: () => (
      <section data-start-section={section.id} data-testid={`start-${section.id}`}>
        {section.id === 'hero' ? (
          sectionBody('hero')
        ) : (
          <>
            <SectionHeader
              id={section.id}
              variant="eyebrow"
              header={t(section.titleKey)}
              tagline={t(SECTION_META[section.id].eyebrowKey)}
              description={t(bodyKeyFor(section))}
            />
            {sectionBody(section.id)}
          </>
        )}
      </section>
    ),
  }));

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
