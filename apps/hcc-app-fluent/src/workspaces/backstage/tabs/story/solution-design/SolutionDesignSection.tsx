import { useState } from 'react';
import { makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import { CheckmarkCircleRegular } from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import { useCopilotRail } from '../../../../../copilot-rail/rail-context';
import { SectionHeader } from '../../../../shared/narrative/SectionHeader';
import {
  IQ_PLANES,
  buildSolutionDesignInsight,
  buildSolutionDesignReco,
  type Capability,
  type IqPlane,
  type IqPlaneId,
  type SolutionDesignContext,
} from './solution-design-model';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  board: {
    display: 'grid',
    gridTemplateColumns: 'minmax(150px, 0.85fr) minmax(0, 2.6fr) minmax(150px, 0.85fr)',
    gap: tokens.spacingHorizontalM,
    alignItems: 'stretch',
    '@media screen and (max-width: 1000px)': {
      gridTemplateColumns: '1fr',
    },
  },
  layers: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  card: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
  },
  cardHeader: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: '2px',
    padding: 0,
    border: 'none',
    backgroundColor: 'transparent',
    cursor: 'pointer',
    textAlign: 'left',
    fontFamily: 'inherit',
    borderRadius: tokens.borderRadiusSmall,
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: '2px',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
  cardTitle: {
    fontSize: tokens.fontSizeBase400,
    fontWeight: tokens.fontWeightSemibold,
  },
  cardTagline: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
  },
  caps: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
  },
  laneCaps: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: tokens.spacingVerticalXS,
  },
  cap: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    padding: '3px 8px',
    fontSize: tokens.fontSizeBase200,
    borderRadius: tokens.borderRadiusCircular,
    cursor: 'pointer',
    fontFamily: 'inherit',
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: '2px',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '1px',
    },
  },
  capMvp: {
    border: `1px solid transparent`,
    backgroundColor: 'rgba(23, 184, 144, 0.14)',
    color: '#12765F',
  },
  capTarget: {
    border: '1px dashed transparent',
    backgroundColor: 'transparent',
  },
  capActive: {
    outlineStyle: 'solid',
    outlineWidth: '2px',
    outlineColor: tokens.colorStrokeFocus2,
    outlineOffset: '1px',
  },
  checkIcon: {
    fontSize: '12px',
  },
});

interface SelectedState {
  scope: IqPlaneId;
  kind: 'plane' | 'capability';
  capabilityId?: string;
}

/** Sprint 36 intake — the Solution design (IQ operating model) section, routing to the PO Agent rail. */
export function SolutionDesignSection() {
  const s = useStyles();
  const { t } = useTranslation();
  const [selected, setSelected] = useState<SelectedState>({ scope: 'work', kind: 'plane' });
  let rail: ReturnType<typeof useCopilotRail> | null = null;
  try {
    rail = useCopilotRail();
  } catch {
    rail = null;
  }

  const select = (plane: IqPlane, capability?: Capability) => {
    const ctx: SolutionDesignContext = {
      scope: plane.id,
      kind: capability ? 'capability' : 'plane',
      capabilityId: capability?.id,
      tier: capability?.tier,
      source: 'backstage-solution-design',
    };
    setSelected({ scope: plane.id, kind: ctx.kind, capabilityId: capability?.id });
    const label = capability ? `${plane.label} - ${capability.label}` : plane.label;
    rail?.openWithReco(buildSolutionDesignInsight(ctx, label), buildSolutionDesignReco(plane, ctx, t));
  };

  const layers = IQ_PLANES.filter((p) => p.kind === 'layer');
  const gov = IQ_PLANES.find((p) => p.id === 'gov')!;
  const sec = IQ_PLANES.find((p) => p.id === 'sec')!;

  const renderCard = (plane: IqPlane, lane = false) => {
    const planeSelected = selected.scope === plane.id && selected.kind === 'plane';
    return (
      <div key={plane.id} className={s.card} style={{ borderLeftColor: plane.accent }}>
        <button
          type="button"
          className={s.cardHeader}
          aria-pressed={planeSelected}
          onClick={() => select(plane)}
        >
          <span className={s.cardTitle} style={{ color: plane.text }}>
            {plane.label}
          </span>
          <span className={s.cardTagline}>{plane.tagline}</span>
        </button>
        <div className={lane ? s.laneCaps : s.caps}>
          {plane.capabilities.map((c) => {
            const active = selected.kind === 'capability' && selected.capabilityId === c.id;
            const tierStyle =
              c.tier === 'target'
                ? { borderColor: plane.accent, color: plane.text }
                : undefined;
            return (
              <button
                key={c.id}
                type="button"
                aria-pressed={active}
                className={mergeClasses(
                  s.cap,
                  c.tier === 'mvp' ? s.capMvp : s.capTarget,
                  active && s.capActive,
                )}
                style={tierStyle}
                onClick={() => select(plane, c)}
              >
                {c.tier === 'mvp' && <CheckmarkCircleRegular className={s.checkIcon} />}
                {c.label}
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <section
      className={s.root}
      data-testid="solution-design-section"
      aria-labelledby="solution-design-title"
    >
      <SectionHeader
        id="solution-design"
        variant="eyebrow"
        header={t('backstage.story.solutionDesign.header', 'The Microsoft IQ operating model, one governed platform')}
        tagline={t('backstage.story.solutionDesign.tagline', 'Backstage \u00b7 Frontier architecture')}
        description={t(
          'backstage.story.solutionDesign.description',
          'Five IQ layers between a Governance and a Security lane. Select any layer or capability to ask the Product Owner Agent for grounded, cited detail.',
        )}
      />
      <div className={s.board}>
        {renderCard(gov, true)}
        <div className={s.layers}>{layers.map((p) => renderCard(p))}</div>
        {renderCard(sec, true)}
      </div>
    </section>
  );
}
