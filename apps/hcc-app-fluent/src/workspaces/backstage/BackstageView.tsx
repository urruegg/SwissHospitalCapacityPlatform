import type { JSX } from 'react';
import { useParams } from 'react-router-dom';
import { Body1, makeStyles, Title2, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { DigitalFeedbackLoopSection } from './tabs/story/feedback-loop/DigitalFeedbackLoopSection';
import { OpportunityPipelineView } from './opportunity/OpportunityPipelineView';
import {
  BACKSTAGE_PARTS,
  BackstageSubNav,
  DEFAULT_BACKSTAGE_PART,
} from './BackstageSubNav';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalL,
  },
  header: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    maxWidth: '820px',
  },
  lead: {
    color: tokens.colorNeutralForeground2,
  },
});

/**
 * Sprint 35 - Backstage surface.
 *
 * Restructured from the Sprint 20 four-tab layout (Story / Evidence /
 * Opportunities / Roles). The surface now opens on the Curavias Digital
 * Feedback Loop as its first part, with a Main-style sub-nav (`BackstageSubNav`)
 * for additional parts as they land. Each part owns its own content; the view
 * only selects and mounts the active part behind `/backstage/:widget?`.
 */
const PARTS: Record<string, () => JSX.Element> = {
  'feedback-loop': () => (
    <div data-testid="widget-feedback-loop">
      <DigitalFeedbackLoopSection />
    </div>
  ),
  opportunities: () => (
    <div data-testid="widget-opportunities">
      <OpportunityPipelineView />
    </div>
  ),
};

export function BackstageView() {
  const styles = useStyles();
  const { t } = useTranslation();
  const { widget = DEFAULT_BACKSTAGE_PART } = useParams();
  const activePart = BACKSTAGE_PARTS.some((p) => p.key === widget)
    ? widget
    : DEFAULT_BACKSTAGE_PART;
  const Part = PARTS[activePart] ?? PARTS[DEFAULT_BACKSTAGE_PART];

  return (
    <div className={styles.root} data-testid="backstage-surface">
      <header className={styles.header}>
        <Title2>{t('backstage.header.title')}</Title2>
        <Body1 as="p" className={styles.lead}>
          {t('backstage.header.lead')}
        </Body1>
      </header>
      <BackstageSubNav />
      <Part />
    </div>
  );
}
