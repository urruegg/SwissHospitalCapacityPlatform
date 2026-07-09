import { Button } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useRole } from '../../context/role-context';

/**
 * Sprint 13 T4 — role switcher.
 *
 * Hidden unless `env=sit` AND the caller holds `HCC.PlatformAdmin` or
 * `HCC.DemoOperator` (design spec §2.1). Rendering nothing keeps the control
 * out of the accessibility tree for unauthorised users.
 */
export function RoleSwitcher() {
  const { t } = useTranslation();
  const { canSwitchRole } = useRole();
  if (!canSwitchRole) return null;
  return (
    <Button appearance="transparent" aria-label={t('topbar.roleSwitcher')}>
      {t('topbar.roleSwitcher')}
    </Button>
  );
}
