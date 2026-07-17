import { Switch } from '@fluentui/react-components';
import { useThemeMode } from '../../theme/theme-context';

/** Sprint 20 M3 — light/dark toggle bound to the theme-mode context. */
export function ThemeToggle() {
  const { mode, toggle } = useThemeMode();
  return (
    <Switch
      aria-label="Theme"
      checked={mode === 'dark'}
      onChange={toggle}
      label={mode === 'dark' ? 'Dark' : 'Light'}
    />
  );
}
