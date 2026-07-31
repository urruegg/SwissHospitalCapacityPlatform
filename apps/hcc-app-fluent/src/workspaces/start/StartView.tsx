import { Badge, MessageBar, MessageBarBody, makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useMode } from '../../context/mode-context';
import { SectionHeader } from '../shared/narrative/SectionHeader';
import { NarrativeShell, type NarrativeSection } from '../shared/narrative/NarrativeShell';
import { BvaDecisionSection } from './frontier/BvaDecisionSection';
import { CioChallengerSection } from './frontier/CioChallengerSection';
import { HospitalsSection } from './frontier/HospitalsSection';
import { NinetyDaySection } from './frontier/NinetyDaySection';
import { PatientPathLauncher } from './frontier/PatientPathLauncher';
import { StartHero } from './frontier/StartHero';
import { WorkChartSection } from './frontier/WorkChartSection';
import { START_SECTIONS, type StartSection } from './frontier/start-content';

// Per-section eyebrow kicker + nav label (English defaults; DE/FR/IT eyebrows are a follow-up).
const SECTION_META: Record<StartSection['id'], { eyebrow: string; nav: string }> = {
  hero: { eyebrow: '', nav: 'Value' },
  'work-chart': { eyebrow: 'The idea in one minute', nav: 'Operating model' },
  'cio-why-now': { eyebrow: 'The CIO challenge · why now', nav: 'Why now' },
  hospitals: { eyebrow: 'Key visual · Organisation', nav: 'Hospitals' },
  'patient-path': { eyebrow: 'The Curavias patient path', nav: 'Care path' },
  'ninety-day': { eyebrow: 'The first frontier · 90 days', nav: '90-day' },
  bva: { eyebrow: 'The decision · Business Value Assessment', nav: 'BVA' },
};

const useStyles = makeStyles({
  guardrails: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
    alignItems: 'stretch',
  },
  badges: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    alignItems: 'center',
  },
});

function bodyKeyFor(section: StartSection) {
  return section.titleKey.replace(/\.title$/, '.body');
}

function sectionBody(id: StartSection['id'], mode: 'demo' | 'user') {
  switch (id) {
    case 'hero':
      return <StartHero mode={mode} />;
    case 'work-chart':
      return <WorkChartSection />;
    case 'cio-why-now':
      return <CioChallengerSection />;
    case 'hospitals':
      return <HospitalsSection />;
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
 * Backstage surface. Sections, data bindings, and testids are unchanged.
 */
export function StartView() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();

  const guardrails = (
    <div className={s.guardrails}>
      <MessageBar intent="info">
        <MessageBarBody>{t('start.frontier.guardrails.synthetic')}</MessageBarBody>
      </MessageBar>
      <div className={s.badges}>
        <Badge
          appearance="filled"
          color={mode === 'demo' ? 'brand' : 'success'}
          data-testid="start-mode-badge"
        >
          {mode === 'demo' ? t('start.frontier.mode.demo') : t('start.frontier.mode.user')}
        </Badge>
        <Badge appearance="tint" color="informative">
          {t('start.frontier.guardrails.advisory')}
        </Badge>
        <Badge appearance="tint" color="warning">
          {t('start.frontier.guardrails.noPhi')}
        </Badge>
      </div>
    </div>
  );

  const sections: NarrativeSection[] = START_SECTIONS.map((section) => ({
    key: section.id,
    label: SECTION_META[section.id].nav,
    render: () => (
      <section data-start-section={section.id} data-testid={`start-${section.id}`}>
        {section.id === 'hero' ? (
          sectionBody('hero', mode)
        ) : (
          <>
            <SectionHeader
              id={section.id}
              variant="eyebrow"
              header={t(section.titleKey)}
              tagline={SECTION_META[section.id].eyebrow}
              description={t(bodyKeyFor(section))}
            />
            {sectionBody(section.id, mode)}
          </>
        )}
      </section>
    ),
  }));

  return (
    <div data-testid="start-view">
      <NarrativeShell
        introKey="overview"
        introNavLabel={t('start.frontier.nav.overview', 'Overview')}
        introEyebrow={t('start.frontier.page.eyebrow', 'Start · for hospital & healthcare C-level · 5–10 min')}
        introTitle={t('start.frontier.page.title')}
        introDescription={t('start.frontier.page.lead')}
        introExtra={guardrails}
        sections={sections}
        navLabel={t('start.frontier.nav.label', 'Start sections')}
        navTestIdPrefix="start-nav"
        leadingGroupCount={2}
      />
    </div>
  );
}
