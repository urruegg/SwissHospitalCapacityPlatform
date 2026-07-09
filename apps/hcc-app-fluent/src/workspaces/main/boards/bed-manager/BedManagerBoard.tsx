import { useState } from 'react';
import { makeStyles, tokens, Title2, Button } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { Canvas } from '../../../../whiteboard/Canvas';
import { useLayoutManager } from '../../../../whiteboard/LayoutManager';
import { bedManagerCards } from './mock-data';
import { CopilotDrawer } from '../../../../copilot-drawer/Drawer';

const useStyles = makeStyles({
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: tokens.spacingVerticalM,
  },
});

/** Sprint 13 T3/T6 — BedManager @ USZ reference operational whiteboard. */
export function BedManagerBoard() {
  const styles = useStyles();
  const { t } = useTranslation();
  const layout = useLayoutManager(bedManagerCards);
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <section aria-label={t('bedManager.title')}>
      <div className={styles.header}>
        <Title2>{t('bedManager.title')}</Title2>
        <Button appearance="primary" onClick={() => setDrawerOpen(true)}>
          {t('bedManager.askBmca')}
        </Button>
      </div>
      <Canvas layout={layout} />
      <CopilotDrawer
        agent="bmca-agent"
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
      />
    </section>
  );
}
