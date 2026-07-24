import { makeStyles, Text, Title3, tokens } from '@fluentui/react-components';
import { ds } from '../../theme/design-system';
import { useSurfaceStyles, useStateStyles } from '../../theme/design-system/recipes';

/**
 * Sprint 27 M3 — dev-only design-system gallery.
 *
 * Route-only surface (mounted at `/brand`, not in any navigation menu). It
 * renders the semantic spacing/elevation tokens and the shared surface/state
 * recipes so we can eyeball the design system in isolation. Intentionally
 * English-only (no i18n) so it renders under `ThemeModeProvider` alone.
 */
const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: ds.space.xl,
    padding: ds.space.xl,
  },
  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: ds.space.m,
  },
  row: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: ds.space.m,
    alignItems: 'flex-end',
  },
  swatch: {
    display: 'flex',
    flexDirection: 'column',
    gap: ds.space.xs,
    alignItems: 'center',
  },
});

export function BrandGalleryView() {
  const s = useStyles();
  const surface = useSurfaceStyles();
  const state = useStateStyles();

  return (
    <div data-testid="brand-gallery" className={s.root}>
      <section className={s.section} aria-label="Spacing">
        <Title3>Spacing</Title3>
        <div className={s.row}>
          {Object.entries(ds.space).map(([k, v]) => (
            <div key={k} className={s.swatch}>
              <div style={{ width: v, height: v, backgroundColor: tokens.colorBrandBackground }} />
              <Text size={200}>
                {k} · {v}
              </Text>
            </div>
          ))}
        </div>
      </section>

      <section className={s.section} aria-label="Elevation">
        <Title3>Elevation</Title3>
        <div className={s.row}>
          {Object.keys(ds.elevation).map((k) => (
            <div key={k} className={surface.surfaceCard}>
              <Text>{k}</Text>
            </div>
          ))}
        </div>
      </section>

      <section className={s.section} aria-label="Component states">
        <Title3>Component states</Title3>
        <div className={surface.statTile}>
          <Text>statTile</Text>
        </div>
        <div className={surface.provenanceBadge}>
          <Text size={200}>live</Text>
        </div>
        <div className={state.emptyState}>
          <Text>Empty state</Text>
        </div>
        <div className={state.loadingState}>
          <Text>Loading</Text>
        </div>
        <div className={state.errorState}>
          <Text>Error state</Text>
        </div>
      </section>
    </div>
  );
}
