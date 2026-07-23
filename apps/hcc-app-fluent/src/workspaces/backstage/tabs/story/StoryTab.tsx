import { Body1, Card, makeStyles, Text, Title2, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { STORY_PILLARS } from './story-content';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalL,
  },
  header: {
    maxWidth: '760px',
  },
  lead: {
    marginTop: tokens.spacingVerticalS,
  },
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
});

export function StoryTab() {
  const styles = useStyles();
  const { t } = useTranslation();

  return (
    <section className={styles.root} data-testid="backstage-story" aria-labelledby="backstage-story-title">
      <div className={styles.header}>
        <Title2 id="backstage-story-title">{t('backstage.story.title', 'How Curavias is built')}</Title2>
        <Body1 as="p" className={styles.lead}>
          {t('backstage.story.lead')}
        </Body1>
      </div>
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
  );
}
