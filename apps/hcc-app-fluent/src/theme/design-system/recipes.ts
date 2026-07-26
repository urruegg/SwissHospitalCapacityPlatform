import { makeStyles, tokens } from '@fluentui/react-components';
import { space, radii, elevation, motion, focus } from './tokens';

export const useSurfaceStyles = makeStyles({
  surfaceCard: {
    backgroundColor: tokens.colorNeutralBackground1,
    borderRadius: radii.card,
    boxShadow: elevation.card,
    padding: space.l,
    transitionDuration: motion.durationNormal,
    transitionTimingFunction: motion.easyEase,
    ':hover': { boxShadow: elevation.raised },
    ':focus-within': {
      outlineWidth: focus.ringWidth,
      outlineStyle: 'solid',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: focus.ringOffset,
    },
  },
  boardGrid: { display: 'grid', gap: space.l, gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: space.m,
    marginBottom: space.m,
  },
  statTile: { display: 'flex', flexDirection: 'column', gap: space.xs, padding: space.m, borderRadius: radii.control },
  provenanceBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: space.xs,
    padding: `${space.xs} ${space.s}`,
    borderRadius: radii.pill,
  },
});

export const useStateStyles = makeStyles({
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: space.m, padding: space.xxl },
  loadingState: { display: 'flex', alignItems: 'center', gap: space.s, padding: space.xl },
  errorState: {
    display: 'flex',
    flexDirection: 'column',
    gap: space.s,
    padding: space.l,
    borderRadius: radii.control,
    color: tokens.colorPaletteRedForeground1,
  },
});
