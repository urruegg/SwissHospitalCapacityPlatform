import {
  Body1,
  Button,
  Text,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { Trans, useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { scrollToSection } from '../../shared/narrative/NarrativeShell';
import { SHOWCASE_ACCENT, useShowcaseStyles } from '../../shared/narrative/showcase-styles';

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
  leadEmphasis: {
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  quote: {
    margin: 0,
    fontStyle: 'italic',
    fontWeight: tokens.fontWeightSemibold,
    // Fluent's link-foreground token keeps WCAG contrast in both themes for this accent line.
    color: tokens.colorBrandForegroundLink,
  },
  frameTitle: {
    margin: 0,
    fontSize: tokens.fontSizeBase300,
    fontWeight: tokens.fontWeightBold,
    color: SHOWCASE_ACCENT.navy,
  },
  frameBody: {
    margin: 0,
    fontSize: tokens.fontSizeBase200,
    lineHeight: 1.5,
    color: tokens.colorNeutralForeground2,
  },
  frameEmph: {
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  ctas: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    alignItems: 'center',
  },
});

export function StartHero() {
  const styles = useStyles();
  const showcase = useShowcaseStyles();
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className={styles.root}>
      <span className={styles.eyebrow}>{t('start.frontier.hero.eyebrow')}</span>
      <h2 className={styles.hook}>
        <span className={styles.hookInk}>{t('start.frontier.hero.hookPrefix')}</span>
        <span className={styles.hookAccent}>{t('start.frontier.hero.hookAccent')}</span>
      </h2>
      <Body1 as="p" className={styles.lead}>
        {t('start.frontier.hero.leadPrefix')}
        <span className={styles.leadEmphasis}>{t('start.frontier.hero.leadEmphasis')}</span>
        {t('start.frontier.hero.leadSuffix')}
      </Body1>
      <Text as="p" className={styles.quote} data-testid="hero-quote">
        {t('start.frontier.hero.quote')}
      </Text>

      <div
        className={showcase.staticCard}
        style={{ borderLeftColor: SHOWCASE_ACCENT.navy }}
        data-testid="hero-framebox"
      >
        <p className={styles.frameTitle}>{t('start.frontier.hero.framebox.title')}</p>
        <p className={styles.frameBody}>
          <Trans
            i18nKey="start.frontier.hero.framebox.body"
            components={{ b: <span className={styles.frameEmph} /> }}
          />
        </p>
      </div>

      <div className={styles.ctas}>
        <Button appearance="primary" onClick={() => scrollToSection('challenger')}>
          {t('start.frontier.hero.ctaPrimary')}
        </Button>
        <Button appearance="secondary" onClick={() => scrollToSection('hospitals')}>
          {t('start.frontier.hero.ctaHospitals')}
        </Button>
        <Button appearance="secondary" onClick={() => navigate('/backstage')}>
          {t('start.frontier.hero.ctaBackstage')}
        </Button>
      </div>
    </div>
  );
}
