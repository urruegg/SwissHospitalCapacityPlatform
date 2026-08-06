import {
  Body1,
  Caption1,
  Link,
  Text,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import { scrollToSection } from '../../shared/narrative/NarrativeShell';

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
    alignContent: 'start',
  },
  eyebrow: {
    // Backstage SectionHeader eyebrow pattern: uppercase kicker + green lead bar.
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    color: '#12765F',
    '::before': {
      content: '""',
      width: '22px',
      height: '3px',
      borderRadius: '2px',
      backgroundColor: '#17B890',
    },
  },
  hook: {
    // Match the Backstage hero headline (SectionHeader headerLg): base600 on a plain
    // h2, no width cap, so the title fills the column on one line instead of a narrow stack.
    margin: 0,
    fontSize: tokens.fontSizeBase600,
    lineHeight: tokens.lineHeightBase600,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  hookInk: {
    color: tokens.colorNeutralForeground1,
  },
  hookAccent: {
    backgroundImage: 'linear-gradient(110deg, #365B7D, #17B890 78%)',
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    color: 'transparent',
  },
  lead: {
    // No width cap — matches the Backstage SectionHeader description, so the lead flows
    // the full column width rather than being squeezed into a narrow left measure.
    color: tokens.colorNeutralForeground2,
  },
  quote: {
    margin: 0,
    fontStyle: 'italic',
    fontWeight: tokens.fontWeightSemibold,
    // Fluent's link-foreground token keeps WCAG contrast in both themes for this accent line.
    color: tokens.colorBrandForegroundLink,
  },
  trustPills: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
  },
  pill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    padding: `${tokens.spacingVerticalXXS} ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusCircular,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground2,
  },
  pillDot: {
    width: '8px',
    height: '8px',
    borderRadius: tokens.borderRadiusCircular,
    backgroundColor: tokens.colorPaletteGreenForeground1,
    flexShrink: 0,
  },
  pillLabel: {
    color: tokens.colorNeutralForeground1,
    fontWeight: tokens.fontWeightSemibold,
  },
  ctas: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    alignItems: 'center',
  },
  ctaLink: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '40px',
    padding: `${tokens.spacingVerticalXS} ${tokens.spacingHorizontalM}`,
    borderRadius: tokens.borderRadiusMedium,
    fontWeight: tokens.fontWeightSemibold,
    textDecorationLine: 'none',
    border: 'none',
    backgroundColor: 'transparent',
    cursor: 'pointer',
    font: 'inherit',
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
  ctaPrimary: {
    backgroundColor: tokens.colorBrandBackground,
    color: tokens.colorNeutralForegroundOnBrand,
  },
  ctaSecondary: {
    border: `1px solid ${tokens.colorNeutralStroke1}`,
    color: tokens.colorBrandForegroundLink,
  },
  disclaimer: {
    color: tokens.colorNeutralForeground3,
    display: 'block',
  },
});

export function StartHero() {
  const styles = useStyles();
  const { t } = useTranslation();

  return (
    <div className={styles.root}>
      <span className={styles.eyebrow}>{t('start.frontier.hero.eyebrow')}</span>
      <h2 className={styles.hook}>
        <span className={styles.hookInk}>{t('start.frontier.hero.hookPrefix')}</span>
        <span className={styles.hookAccent}>{t('start.frontier.hero.hookAccent')}</span>
        <span className={styles.hookInk}>{t('start.frontier.hero.hookSuffix')}</span>
      </h2>
      <Body1 as="p" className={styles.lead}>
        {t('start.frontier.hero.leadBeforeJournai')}
        <Link href="https://www.journai.ch/" target="_blank" rel="noopener noreferrer">
          {t('start.frontier.hero.journaiName')}
        </Link>
        {t('start.frontier.hero.leadAfterJournai')}
      </Body1>
      <Text as="p" className={styles.quote} data-testid="hero-quote">
        {t('start.frontier.hero.quote')}
      </Text>

      <div className={styles.trustPills}>
        <span className={styles.pill}>
          <span className={styles.pillDot} aria-hidden="true" />
          <Text size={200}>
            <span className={styles.pillLabel}>{t('start.frontier.hero.pills.advisory.label')}</span>
            {' · '}
            {t('start.frontier.hero.pills.advisory.desc')}
          </Text>
        </span>
        <span className={styles.pill}>
          <span aria-hidden="true">🇨🇭</span>
          <Text size={200}>
            <span className={styles.pillLabel}>{t('start.frontier.hero.pills.swiss.label')}</span>
            {' · '}
            {t('start.frontier.hero.pills.swiss.desc')}
          </Text>
        </span>
        <span className={styles.pill}>
          <span aria-hidden="true">✅</span>
          <Text size={200}>
            {t('start.frontier.hero.pills.live.lead')}{' '}
            <span className={styles.pillLabel}>{t('start.frontier.hero.pills.live.label')}</span>
            {' · '}
            {t('start.frontier.hero.pills.live.desc')}
          </Text>
        </span>
      </div>

      <div className={styles.ctas}>
        <button
          type="button"
          className={mergeClasses(styles.ctaLink, styles.ctaPrimary)}
          onClick={() => scrollToSection('hospitals')}
        >
          {t('start.frontier.hero.ctaPrimary')}
        </button>
        <RouterLink to="/backstage" className={mergeClasses(styles.ctaLink, styles.ctaSecondary)}>
          {t('start.frontier.hero.ctaSecondary')}
        </RouterLink>
      </div>

      <Caption1 className={styles.disclaimer}>
        {t('start.frontier.guardrails.synthetic')} {t('start.frontier.guardrails.advisory')}
      </Caption1>
    </div>
  );
}
