import { useMemo, useState } from 'react';
import {
  makeStyles,
  tokens,
  Title2,
  Body1,
  Badge,
  TabList,
  Tab,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { Canvas } from '../../../../whiteboard/Canvas';
import { useLayoutManager } from '../../../../whiteboard/LayoutManager';
import { evidenceLayouts, loadEvidenceDataset, type EvidencePreset } from '../../../../data/evidence/evidence-service';

const useStyles = makeStyles({
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: tokens.spacingVerticalM,
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalM,
  },
  summary: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    marginBottom: tokens.spacingVerticalM,
    flexWrap: 'wrap',
  },
});

/**
 * Sprint 14.1 · T6 — Backstage "Evidence" tab.
 *
 * Composes the Sprint 13 whiteboard framework with the Evidence card registry
 * (BOM / ADR / PRD-requirement / GA-evidence / dependency-edge). Reads the
 * committed evidence dataset (design spec §4/§5; ADR-0026) and offers the two
 * preset presenter layouts. Provenance is enforced per-card by the card
 * components themselves.
 */
export function EvidenceTab() {
  const styles = useStyles();
  const { t } = useTranslation();
  const dataset = useMemo(() => loadEvidenceDataset(), []);
  const layouts = useMemo(() => evidenceLayouts(dataset), [dataset]);
  const [preset, setPreset] = useState<EvidencePreset>('ch-north-tshow');

  const active = layouts.find((l) => l.key === preset) ?? layouts[0];
  const layout = useLayoutManager(active.cards);

  const summaryByTrack = useMemo(() => {
    const map = new Map(dataset.summary.map((s) => [s.track, s]));
    return map;
  }, [dataset]);

  const tShow = summaryByTrack.get('T-SHOW');
  const tProd = summaryByTrack.get('T-PROD');
  const gap = summaryByTrack.get('GA-parity-gap');

  return (
    <section aria-label={t('backstage.evidence')}>
      <div className={styles.header}>
        <div>
          <Title2>{t('backstage.evidence')}</Title2>
          <Body1 as="p">{t('backstage.evidenceDescription')}</Body1>
        </div>
        <TabList
          selectedValue={preset}
          onTabSelect={(_e, data) => {
            const next = data.value as EvidencePreset;
            setPreset(next);
            const nextLayout = layouts.find((l) => l.key === next);
            if (nextLayout) layout.reset(nextLayout.cards);
          }}
        >
          {layouts.map((l) => (
            <Tab key={l.key} value={l.key}>
              {t(l.labelKey)}
            </Tab>
          ))}
        </TabList>
      </div>

      <div className={styles.summary} aria-label={t('evidence.readinessSummary')}>
        <Badge appearance="tint" color="success">
          T-SHOW {tShow ? `${tShow.readyPct}%` : 'n/a'}
        </Badge>
        <Badge appearance="tint" color="warning">
          T-PROD {tProd ? `${tProd.readyPct}%` : 'n/a'}
        </Badge>
        <Badge appearance="tint" color="informative">
          {t('evidence.gaParityGap')}: {gap ? gap.readyCount : 'n/a'}
        </Badge>
        <Badge appearance="outline">{dataset.boms.length} BOM</Badge>
        <Badge appearance="outline">{dataset.adrs.length} ADR</Badge>
      </div>

      <Canvas layout={layout} />
    </section>
  );
}
