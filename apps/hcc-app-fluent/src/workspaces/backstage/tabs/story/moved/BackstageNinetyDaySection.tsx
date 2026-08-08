import { makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { SectionHeader } from '../../../../shared/narrative/SectionHeader';
import { NinetyDaySection } from '../../../../start/frontier/NinetyDaySection';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalL },
});

export function BackstageNinetyDaySection() {
  const { t } = useTranslation();
  const styles = useStyles();
  const title = t(
    'backstage.story.ninetyDay.title',
    'Your first frontier: capacity forecast in 90 days',
  );
  const accent = t('backstage.story.ninetyDay.accent', '90 days');
  const parts = title.includes(accent)
    ? [
        { text: title.slice(0, title.indexOf(accent)) },
        { text: accent, tone: 'accent' as const },
        { text: title.slice(title.indexOf(accent) + accent.length) },
      ].filter((part) => part.text.length > 0)
    : [{ text: title }];

  return (
    <section data-testid="backstage-ninety-day-section" className={styles.root} aria-labelledby="ninety-day-title">
      <SectionHeader
        id="ninety-day"
        variant="eyebrow"
        tagline={t('backstage.story.ninetyDay.eyebrow', 'Backstage · the first frontier')}
        titleParts={parts}
        description={t(
          'backstage.story.ninetyDay.lead',
          'The repeatable path a new provider follows — from aligned decisions to a governed, live forecast.',
        )}
      />
      <NinetyDaySection />
    </section>
  );
}
