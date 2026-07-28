import { Menu, MenuTrigger, MenuPopover, MenuList, MenuItem, Button, Badge } from '@fluentui/react-components';
import { PersonRegular, SignOutRegular, ArrowEnterRegular } from '@fluentui/react-icons';
import { useAuthSession } from '../../auth/auth-session';
import { resetSessionContext } from '../../context/session-reset';

/**
 * Sprint 20 M3 / Sprint 27 / Sprint 29 — user menu bound to the auth session.
 * Shows the signed-in account, or the read-only Demo Guest when signed out, and
 * offers Sign in / Sign out against the MngEnvMCAP164444 tenant when MSAL is
 * configured. Sign-out clears all per-user session context — every (user x
 * agent) conversation thread, the Foundry thread map, and the IQ ContextEnvelope
 * (Sprint 29 #424 M1) — so a subsequent session never inherits a prior user's
 * context or data scope.
 */
export function UserMenu() {
  const { name, isAuthenticated, readOnly, configured, signIn, signOut } = useAuthSession();

  const handleSignOut = () => {
    resetSessionContext();
    signOut();
  };

  return (
    <Menu>
      <MenuTrigger disableButtonEnhancement>
        <Button aria-label="User menu" icon={<PersonRegular />} appearance="subtle">
          {name}
          {readOnly && (
            <Badge appearance="tint" color="informative" size="small" style={{ marginLeft: 8 }}>
              read-only
            </Badge>
          )}
        </Button>
      </MenuTrigger>
      <MenuPopover>
        <MenuList>
          {isAuthenticated ? (
            <MenuItem icon={<SignOutRegular />} onClick={handleSignOut}>
              Sign out
            </MenuItem>
          ) : configured ? (
            <MenuItem icon={<ArrowEnterRegular />} onClick={signIn}>
              Sign in
            </MenuItem>
          ) : (
            <MenuItem disabled>Sign-in not configured (demo)</MenuItem>
          )}
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}
