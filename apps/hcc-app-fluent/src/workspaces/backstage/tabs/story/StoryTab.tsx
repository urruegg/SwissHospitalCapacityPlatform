import { useMemo } from 'react';
import {
  Badge,
  Body1,
  Caption1,
  Card,
  Divider,
  makeStyles,
  Text,
  Title2,
  Title3,
  tokens,
} from '@fluentui/react-components';
import { ArrowRightRegular } from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import { loadEvidenceDataset } from '../../../../data/evidence/evidence-service';
import { STORY_PILLARS } from './story-content';
import {
  storyStatTiles,
  COPILOT_ROSTER,
  COPILOT_ROSTER_SOURCE,
  PLAN_TO_RELEASE,
  DEV_TO_PROD,
  type TileProvenance,
} from './story-data';

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXL,
  },
  header: {
    maxWidth: '760px',
  },
  lead: {
    marginTop: tokens.spacingVerticalS,
  },
  sectionTitle: {
    marginBottom: tokens.spacingVerticalS,
  },
  // Pillar cards (unchanged from previous)
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  card: {
    minHeight: '150px',
  },
  cardBody: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
  },
  // Stat tiles
  statGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  statCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingVerticalM,
  },
  statValue: {
    fontSize: tokens.fontSizeHero700,
    fontWeight: tokens.fontWeightBold,
    lineHeight: '1',
  },
  statMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    flexWrap: 'wrap',
    marginTop: tokens.spacingVerticalXS,
  },
  // Delivery strips
  strip: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    flexWrap: 'wrap',
  },
  stageCard: {
    padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
    display: 'inline-flex',
    alignItems: 'center',
  },
  // Copilot roster
  rosterGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: tokens.spacingHorizontalS,
  },
  rosterCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingVerticalS,
  },
  rosterMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
  },
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function provenanceBadgeColor(p: TileProvenance): 'subtle' | 'success' | 'informative' {
  if (p === 'live') return 'success';
  if (p === 'invariant') return 'informative';
  return 'subtle';
}

function ceilingBadgeColor(ceiling: string): 'subtle' | 'warning' | 'danger' | 'important' {
  if (ceiling === 'deploy') return 'warning';
  if (ceiling === 'delete') return 'danger';
  if (ceiling === 'write')  return 'important';
  return 'subtle';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function StoryTab() {
  const styles = useStyles();
  const { t } = useTranslation();

  const dataset = useMemo(() => loadEvidenceDataset(), []);
  const tiles   = useMemo(() => storyStatTiles(dataset), [dataset]);

  return (
    <section className={styles.root} data-testid="backstage-story" aria-labelledby="backstage-story-title">

      {/* ── Header ── */}
      <div className={styles.header}>
        <Title2 id="backstage-story-title">{t('backstage.story.title')}</Title2>
        <Body1 as="p" className={styles.lead}>{t('backstage.story.lead')}</Body1>
      </div>

      {/* ── Stat tiles ── */}
      <section aria-label={t('backstage.story.stats.sectionLabel')}>
        <Title3 className={styles.sectionTitle}>{t('backstage.story.stats.sectionLabel')}</Title3>
        <div className={styles.statGrid} data-testid="story-stat-tiles">
          {tiles.map((tile) => (
            <Card key={tile.id} appearance="filled" className={styles.statCard}>
              <Caption1>{t(tile.labelKey)}</Caption1>
              <Text className={styles.statValue}>{String(tile.value)}</Text>
              <div className={styles.statMeta}>
                <Badge
                  appearance="tint"
                  color={provenanceBadgeColor(tile.provenance)}
                  size="small"
                >
                  {t(`backstage.story.provenance.${tile.provenance}`)}
                </Badge>
                <Caption1>{tile.source} · {tile.asOf}</Caption1>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* ── Delivery strips ── */}
      <section aria-label={t('backstage.story.delivery.sectionLabel')}>
        <Title3 className={styles.sectionTitle}>{t('backstage.story.delivery.sectionLabel')}</Title3>

        {/* PLAN → RELEASE */}
        <div style={{ marginBottom: tokens.spacingVerticalM }}>
          <Caption1 block>{t('backstage.story.delivery.planTitle')}</Caption1>
          <div className={styles.strip} data-testid="story-delivery-plan">
            {PLAN_TO_RELEASE.map((stage, i) => (
              <span key={stage.key} className={styles.strip} style={{ display: 'contents' }}>
                <Card appearance="outline" className={styles.stageCard}>
                  <Text weight="semibold">{t(stage.labelKey)}</Text>
                </Card>
                {i < PLAN_TO_RELEASE.length - 1 && (
                  <ArrowRightRegular aria-hidden="true" />
                )}
              </span>
            ))}
          </div>
        </div>

        <Divider />

        {/* DEV → PROD */}
        <div style={{ marginTop: tokens.spacingVerticalM }}>
          <Caption1 block>{t('backstage.story.delivery.envTitle')}</Caption1>
          <div className={styles.strip} data-testid="story-delivery-env">
            {DEV_TO_PROD.map((stage, i) => (
              <span key={stage.key} className={styles.strip} style={{ display: 'contents' }}>
                <Card appearance="outline" className={styles.stageCard}>
                  <Text weight="semibold">{t(stage.labelKey)}</Text>
                </Card>
                {i < DEV_TO_PROD.length - 1 && (
                  <ArrowRightRegular aria-hidden="true" />
                )}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── Copilot roster ── */}
      <section aria-label={t('backstage.story.roster.sectionLabel')}>
        <Title3 className={styles.sectionTitle}>{t('backstage.story.roster.sectionLabel')}</Title3>
        <Caption1 block style={{ marginBottom: tokens.spacingVerticalS }}>
          {t('backstage.story.roster.countCaption', { count: COPILOT_ROSTER.length })}
          {' · '}{COPILOT_ROSTER_SOURCE}
        </Caption1>
        <div className={styles.rosterGrid} data-testid="story-copilot-roster">
          {COPILOT_ROSTER.map((agent) => (
            <Card key={agent.name} appearance="filled" className={styles.rosterCard}>
              <Text weight="semibold">{agent.displayName}</Text>
              <div className={styles.rosterMeta}>
                <Badge
                  appearance="tint"
                  color={ceilingBadgeColor(agent.ceiling)}
                  size="small"
                >
                  {agent.ceiling}
                </Badge>
                <Caption1>{t(`backstage.story.roster.lane.${agent.name}`, agent.lane)}</Caption1>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* ── Platform pillars (keep existing) ── */}
      <section aria-label={t('backstage.story.pillars.sectionLabel')}>
        <Title3 className={styles.sectionTitle}>{t('backstage.story.pillars.sectionLabel')}</Title3>
        <div className={styles.grid}>
          {STORY_PILLARS.map((pillar) => (
            <Card
              key={pillar.key}
              className={styles.card}
              appearance="filled"
              data-testid={`story-pillar-${pillar.key}`}
            >
              <div className={styles.cardBody}>
                <Text weight="semibold">{t(pillar.titleKey)}</Text>
                <Body1>{t(pillar.bodyKey)}</Body1>
              </div>
            </Card>
          ))}
        </div>
      </section>

    </section>
  );
}
