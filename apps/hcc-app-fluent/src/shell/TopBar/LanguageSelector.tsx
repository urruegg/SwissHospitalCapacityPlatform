import { Menu, MenuTrigger, MenuButton, MenuPopover, MenuList, MenuItemRadio } from '@fluentui/react-components';
import { GlobeRegular } from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';

/** Sprint 20 M3 / Sprint 27 — language selector as an icon menu-button (EN / DE / FR / IT). */
const LANGS = [
  ['de', 'Deutsch'],
  ['en', 'English'],
  ['fr', 'Français'],
  ['it', 'Italiano'],
] as const;

export function LanguageSelector() {
  const { i18n } = useTranslation();
  const current = LANGS.find(([code]) => code === i18n.language)?.[1] ?? i18n.language;
  return (
    <Menu
      checkedValues={{ lang: [i18n.language] }}
      onCheckedValueChange={(_e, d) => {
        const next = d.checkedItems[0];
        if (next) void i18n.changeLanguage(next);
      }}
    >
      <MenuTrigger disableButtonEnhancement>
        <MenuButton aria-label="Language" icon={<GlobeRegular />} appearance="subtle">
          {current}
        </MenuButton>
      </MenuTrigger>
      <MenuPopover>
        <MenuList>
          {LANGS.map(([code, label]) => (
            <MenuItemRadio key={code} name="lang" value={code}>
              {label}
            </MenuItemRadio>
          ))}
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}
