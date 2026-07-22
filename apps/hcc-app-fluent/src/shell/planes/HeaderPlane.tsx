import { makeStyles, tokens, Image, Text } from '@fluentui/react-components';
import { ThemeToggle } from '../TopBar/ThemeToggle';
import { LanguageSelector } from '../TopBar/LanguageSelector';
import { HospitalScopeSelector } from '../TopBar/HospitalScopeSelector';
import { RoleLensDropdown } from '../TopBar/RoleLensDropdown';
import { ModeToggle } from '../TopBar/ModeToggle';
import { UserMenu } from '../TopBar/UserMenu';

const useStyles = makeStyles({
  bar: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
    padding: `0 ${tokens.spacingHorizontalL}`,
    height: '48px',
    backgroundColor: tokens.colorBrandBackground2,
  },
  brand: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalS },
  spacer: { flexGrow: 1 },
  controls: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalM },
});

/**
 * Sprint 20 M3 — AppHeaderPlane.
 *
 * Brand on the left (Curavias icon + wordmark); the five controls are grouped
 * on the right and read Theme, Language, Hospital, Role, User from right to
 * left of the window edge (design spec §2.1 / §7).
 */
export function HeaderPlane() {
  const s = useStyles();
  return (
    <header role="banner" className={s.bar}>
      <div className={s.brand}>
        <Image src="/brand/curavias-icon.svg" alt="Curavias" height={24} width={24} />
        <Text weight="semibold">Curavias</Text>
      </div>
      <div className={s.spacer} />
      <div className={s.controls}>
        <ThemeToggle />
        <LanguageSelector />
        <HospitalScopeSelector />
        <RoleLensDropdown />
        <ModeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
