import { makeStyles, tokens, Title2, Body1 } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import type { WorkspaceKey } from './AppRail';
import { BedManagerBoard } from '../workspaces/main/boards/bed-manager/BedManagerBoard';
import { BackstageRouter } from '../workspaces/backstage/BackstageRouter';
import { CsaWizard } from '../workspaces/main/wizards/csa/CsaWizard';

const useStyles = makeStyles({
  root: {
    flexGrow: 1,
    padding: tokens.spacingHorizontalXL,
    overflow: 'auto',
  },
});

/** Sprint 13 T1 — routes the selected rail workspace to its surface. */
export function WorkspaceRouter({ selected }: { selected: WorkspaceKey }) {
  const styles = useStyles();
  const { t } = useTranslation();
  return (
    <main className={styles.root} role="main" data-workspace={selected}>
      {selected === 'main' && <BedManagerBoard />}
      {selected === 'csa' && <CsaWizard />}
      {selected === 'backstage' && <BackstageRouter />}
      {selected === 'home' && (
        <>
          <Title2>{t('rail.home')}</Title2>
          <Body1 as="p">{t('app.title')}</Body1>
        </>
      )}
      {selected === 'askAgent' && <Title2>{t('rail.askAgent')}</Title2>}
      {selected === 'settings' && <Title2>{t('rail.settings')}</Title2>}
    </main>
  );
}
