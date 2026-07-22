import { Switch } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useMode } from '../../context/mode-context';

/**
 * Sprint 1 (parity) — header ribbon Demo/User toggle. Switches ONLY the handoff
 * orchestration; the data/agent layer is identical in both modes.
 */
export function ModeToggle() {
  const { t } = useTranslation();
  const { mode, setMode } = useMode();
  return (
    <Switch
      checked={mode === 'demo'}
      aria-label={t('mode.toggle', 'Demo mode')}
      label={mode === 'demo' ? t('mode.demo', 'Demo') : t('mode.user', 'User')}
      onChange={(_e, d) => setMode(d.checked ? 'demo' : 'user')}
    />
  );
}
