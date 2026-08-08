import { makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { SectionHeader } from '../../../../shared/narrative/SectionHeader';
import { BvaDecisionSection } from '../../../../start/frontier/BvaDecisionSection';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalL },
});

export function BackstageBvaSection() {
  const { t } = useTranslation();
  const styles = useStyles();
  const title = t(
    'backstage.story.bva.title',
    'We ran a BVA on ourselves before writing a line of code',
  );
  const accent = t('backstage.story.bva.accent', 'BVA on ourselves');
  const parts = title.includes(accent)
    ? [
        { text: title.slice(0, title.indexOf(accent)) },
        { text: accent, tone: 'accent' as const },
        { text: title.slice(title.indexOf(accent) + accent.length) },
      ].filter((part) => part.text.length > 0)
    : [{ text: title }];

  return (
    <section data-testid="backstage-bva-section" className={styles.root} aria-labelledby="bva-title">
      <SectionHeader
        id="bva"
        variant="eyebrow"
        tagline={t('backstage.story.bva.eyebrow', 'Backstage · the business case')}
        titleParts={parts}
        description={t(
          'backstage.story.bva.lead',
          'Before a line of code, Curavias ran a business value assessment on itself — the same discipline it brings to a hospital.',
        )}
      />
      <BvaDecisionSection />
    </section>
  );
}
