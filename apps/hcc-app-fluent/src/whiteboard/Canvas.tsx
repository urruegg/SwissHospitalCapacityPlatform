import { makeStyles, tokens } from '@fluentui/react-components';
import type { CardModel } from '../cards/card-types';
import { resolveCard } from './CardRegistry';
import type { LayoutManager } from './LayoutManager';

/**
 * Sprint 13 T3 — infinite-canvas whiteboard (custom base).
 *
 * Per the whiteboard-base mini-ADR (docs/adr/0021-*), a lightweight custom
 * absolutely-positioned canvas is used instead of React Flow / tldraw to avoid a
 * heavy dependency for the Sprint 13 reference board. Cards render through the
 * registry, so the base can be swapped behind this component if a future board
 * needs edges/zoom.
 */
const useStyles = makeStyles({
  canvas: {
    position: 'relative',
    width: '100%',
    minHeight: '520px',
    backgroundColor: tokens.colorNeutralBackground1,
    backgroundImage: `radial-gradient(${tokens.colorNeutralStroke2} 1px, transparent 1px)`,
    backgroundSize: '24px 24px',
    borderRadius: tokens.borderRadiusMedium,
    overflow: 'auto',
  },
  card: {
    position: 'absolute',
  },
});

export function Canvas({ layout }: { layout: LayoutManager }) {
  const styles = useStyles();
  return (
    <div className={styles.canvas} role="group" aria-label="whiteboard">
      {layout.cards.map((card: CardModel) => {
        const CardComponent = resolveCard(card.type);
        return (
          <div
            key={card.id}
            className={styles.card}
            style={{ left: card.position.x, top: card.position.y }}
            data-card-id={card.id}
          >
            <CardComponent card={card} />
          </div>
        );
      })}
    </div>
  );
}
