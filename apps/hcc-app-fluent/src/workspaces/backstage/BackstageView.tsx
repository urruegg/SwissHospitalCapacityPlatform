import type { JSX } from 'react';
import { Link, useParams } from 'react-router-dom';
import { makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { EvidenceTab } from './tabs/evidence/EvidenceTab';
import { RolesTab } from './tabs/roles/RolesTab';
import { StoryTab } from './tabs/story/StoryTab';
import { OpportunityPipelineView } from './opportunity/OpportunityPipelineView';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalL,
  },
  nav: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
  },
  navLink: {
    color: tokens.colorBrandForegroundLink,
    textDecorationLine: 'none',
    padding: `${tokens.spacingVerticalXS} ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusMedium,
    ':hover': {
      textDecorationLine: 'underline',
    },
  },
  activeNavLink: {
    backgroundColor: tokens.colorBrandBackground,
    color: tokens.colorNeutralForegroundOnBrand,
    fontWeight: tokens.fontWeightSemibold,
  },
});

const NAV_ITEMS = [
  { key: 'story', to: '/backstage/story', labelKey: 'backstage.story.tab' },
  { key: 'evidence', to: '/backstage/evidence', labelKey: 'backstage.evidence' },
  { key: 'opportunities', to: '/backstage/opportunities', labelKey: 'backstage.opportunities' },
  { key: 'roles', to: '/backstage/roles', labelKey: 'backstage.roles' },
];

/**
 * Sprint 20 M5 — Backstage surface.
 *
 * Routes the existing evidence / roles tabs as widgets behind
 * `/backstage/:widget?`, defaulting to the evidence widget. Each tab owns its
 * own whiteboard `Canvas` (evidence) or content, so BackstageView only selects
 * and mounts the widget.
 */
const WIDGETS: Record<string, () => JSX.Element> = {
  story: () => (
    <div data-testid="widget-story">
      <StoryTab />
    </div>
  ),
  evidence: () => (
    <div data-testid="widget-evidence">
      <EvidenceTab />
    </div>
  ),
  opportunities: () => (
    <div data-testid="widget-opportunities">
      <OpportunityPipelineView />
    </div>
  ),
  roles: () => (
    <div data-testid="widget-roles">
      <RolesTab />
    </div>
  ),
};

export function BackstageView() {
  const styles = useStyles();
  const { t } = useTranslation();
  const { widget = 'evidence' } = useParams();
  const W = WIDGETS[widget] ?? WIDGETS.evidence;
  const selectedWidget = WIDGETS[widget] ? widget : 'evidence';

  return (
    <div className={styles.root}>
      <nav className={styles.nav} aria-label={t('backstage.nav.label', 'Backstage sections')}>
        {NAV_ITEMS.map((item) => {
          const active = item.key === selectedWidget;
          return (
            <Link
              key={item.key}
              to={item.to}
              data-testid={`backstage-nav-${item.key}`}
              className={mergeClasses(styles.navLink, active && styles.activeNavLink)}
              aria-current={active ? 'page' : undefined}
            >
              {t(item.labelKey)}
            </Link>
          );
        })}
      </nav>
      <W />
    </div>
  );
}
