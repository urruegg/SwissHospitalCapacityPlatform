import { useState } from 'react';
import {
  makeStyles,
  tokens,
  Text,
  Menu,
  MenuTrigger,
  MenuButton,
  MenuPopover,
  MenuList,
  MenuItemRadio,
} from '@fluentui/react-components';
import { ArrowSyncRegular } from '@fluentui/react-icons';
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
 * Sprint 20 M8 / Sprint 27 — footer plane.
 *
 * Right-aligned bar with the real-time refresh-rate selector (as an icon
 * menu-button matching the header selectors) and the build-time app version.
 */
export function FooterPlane() {
  const s = useStyles();
  const [rate, setRate] = useState('off');
  const label = RATES.find(([v]) => v === rate)?.[1] ?? 'Off';
  return (
    <footer role="contentinfo" className={s.bar}>
      <Menu
        checkedValues={{ rate: [rate] }}
        onCheckedValueChange={(_e, d) => setRate(d.checkedItems[0] ?? 'off')}
      >
        <MenuTrigger disableButtonEnhancement>
          <MenuButton aria-label="Refresh rate" icon={<ArrowSyncRegular />} appearance="subtle" size="small">
            {label}
          </MenuButton>
        </MenuTrigger>
        <MenuPopover>
          <MenuList>
            {RATES.map(([v, l]) => (
              <MenuItemRadio key={v} name="rate" value={v}>
                {l}
              </MenuItemRadio>
            ))}
          </MenuList>
        </MenuPopover>
      </Menu>
      <Text size={200}>{`v${APP_VERSION}`}</Text>
    </footer>
  );
}
