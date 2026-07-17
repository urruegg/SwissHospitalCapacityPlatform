import { Dropdown, Option } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';

/** Sprint 20 M3 — language selector (EN / DE / FR / IT per design spec §2.1). */
const LANGS = [
  ['de', 'Deutsch'],
  ['en', 'English'],
  ['fr', 'Français'],
  ['it', 'Italiano'],
] as const;

export function LanguageSelector() {
  const { i18n } = useTranslation();
  return (
    <Dropdown
      aria-label="Language"
      value={i18n.language}
      selectedOptions={[i18n.language]}
      onOptionSelect={(_e, d) => {
        if (d.optionValue) void i18n.changeLanguage(d.optionValue);
      }}
    >
      {LANGS.map(([code, label]) => (
        <Option key={code} value={code}>
          {label}
        </Option>
      ))}
    </Dropdown>
  );
}
