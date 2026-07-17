import { makeStyles, tokens, Text, Dropdown, Option } from '@fluentui/react-components';
import { APP_VERSION } from '../../config/app-version';

const useStyles = makeStyles({
  bar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: tokens.spacingHorizontalM,
    height: '28px',
    padding: `0 ${tokens.spacingHorizontalL}`,
    backgroundColor: tokens.colorNeutralBackground3,
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
  },
});

const RATES = [
  ['off', 'Off'],
  ['30', '30s'],
  ['60', '60s'],
  ['300', '5m'],
] as const;

/**
 * Sprint 20 M8 — footer plane.
 *
 * Right-aligned bar showing the real-time refresh-rate selector (used by
 * live AppMainPlane surfaces) and the build-time app version.
 */
export function FooterPlane() {
  const s = useStyles();
  return (
    <footer role="contentinfo" className={s.bar}>
      <Dropdown
        aria-label="Refresh rate"
        size="small"
        defaultValue="Off"
        defaultSelectedOptions={['off']}
      >
        {RATES.map(([v, l]) => (
          <Option key={v} value={v}>
            {l}
          </Option>
        ))}
      </Dropdown>
      <Text size={200}>{`v${APP_VERSION}`}</Text>
    </footer>
  );
}
