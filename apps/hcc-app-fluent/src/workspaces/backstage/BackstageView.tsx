import type { JSX } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { DigitalFeedbackLoopSection } from './tabs/story/feedback-loop/DigitalFeedbackLoopSection';
import { SolutionDesignSection } from './tabs/story/solution-design/SolutionDesignSection';
import { BackstageBvaSection } from './tabs/story/moved/BackstageBvaSection';
import { BackstageNinetyDaySection } from './tabs/story/moved/BackstageNinetyDaySection';
import {
  SuccessFrameworkSection,
  DevSecOpsLoopSection,
  ReviewSessionsSection,
  PoKnowledgeClassesSection,
} from './tabs/story/narrative/BackstageNarrativeSections';
import { NarrativeShell, type NarrativeSection } from '../shared/narrative/NarrativeShell';
import { BACKSTAGE_PARTS } from './BackstageSubNav';

/**
 * Sprint 38 - Backstage as a vertical scroll narrative.
 *
 * The surface stacks its story sections on one
 * scrollable page with a sticky Main-style section nav (scrollspy) provided by
 * `NarrativeShell`. `/backstage/:widget` deep-links scroll to the matching
 * section on mount.
 */
const RENDERERS: Record<string, () => JSX.Element> = {
  bva: () => <BackstageBvaSection />,
  'success-framework': () => <SuccessFrameworkSection />,
  'feedback-loop': () => <DigitalFeedbackLoopSection />,
  'solution-design': () => <SolutionDesignSection />,
  'devsecops-loop': () => <DevSecOpsLoopSection />,
  'review-sessions': () => <ReviewSessionsSection />,
  'po-classes': () => <PoKnowledgeClassesSection />,
  'ninety-day': () => <BackstageNinetyDaySection />,
};

export function BackstageView() {
  const { t } = useTranslation();
  const { widget } = useParams();
  const initialKey =
    widget && (widget === 'company' || BACKSTAGE_PARTS.some((p) => p.key === widget))
      ? widget
      : undefined;

  const sections: NarrativeSection[] = BACKSTAGE_PARTS.map((part) => ({
    key: part.key,
    label: t(part.labelKey),
    render: RENDERERS[part.key] ?? (() => <div />),
  }));

  return (
    <div data-testid="backstage-surface">
      <NarrativeShell
        introEyebrow={t('backstage.header.eyebrow', 'Backstage - the company behind the product')}
        introKey="company"
        introNavLabel={t('backstage.nav.company', 'Company')}
        introTitle={t('backstage.header.title')}
        introDescription={t('backstage.header.lead')}
        sections={sections}
        initialKey={initialKey}
        leadingGroupCount={2}
        navLabel={t('backstage.nav.label', 'Backstage sections')}
      />
    </div>
  );
}
