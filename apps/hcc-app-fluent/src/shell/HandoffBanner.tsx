import { Badge, MessageBar, MessageBarBody, makeStyles, tokens } from '@fluentui/react-components';
import { ArrowSyncRegular } from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import type { BannerContext, Provenance } from '../journey/RoleBoard';

const useStyles = makeStyles({
  row: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalS },
  loop: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS },
});

/** Sprint 1 (parity) — leads each role surface; carries the situation forward. */
export function HandoffBanner({
  banner,
  provenance,
}: {
  banner: BannerContext;
  provenance: Provenance;
}) {
  const s = useStyles();
  const { t } = useTranslation();

  return (
    <MessageBar intent="info">
      <MessageBarBody>
        <div className={s.row}>
          <span>{banner.situation}</span>
          <Badge appearance="outline" color={provenance === 'live' ? 'success' : 'warning'}>
            {provenance === 'live' ? t('handoff.live', 'live') : t('handoff.simulated', 'simulated')}
          </Badge>
          {banner.loopBackToOoa ? (
            <span className={s.loop} data-testid="loop-back">
              <ArrowSyncRegular />
              {t('handoff.loopBack', 'loops back to occupancy forecast')}
            </span>
          ) : null}
        </div>
      </MessageBarBody>
    </MessageBar>
  );
}
