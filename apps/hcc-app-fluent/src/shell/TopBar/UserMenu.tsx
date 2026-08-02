import { useState } from 'react';
import { Menu, MenuTrigger, MenuPopover, MenuList, MenuItem, Button, Badge } from '@fluentui/react-components';
import { PersonRegular, SignOutRegular, ArrowEnterRegular, ContactCardRegular } from '@fluentui/react-icons';
import { useAuthSession } from '../../auth/auth-session';
import { useSignOut } from '../../auth/use-sign-out';
import { AccountDialog } from '../account/AccountDialog';

/**
 * Sprint 20 M3 / Sprint 27 / Sprint 29 / Sprint A - user menu bound to the auth
 * session. Shows the signed-in account (or the read-only Demo Guest), a "My
 * account" view of identity + roles when signed in (FR-AUTH-003), and Sign in /
 * Sign out against the MngEnvMCAP164444 tenant when MSAL is configured. Sign-out
 * clears all per-user session context (Sprint 29 #424 M1).
 */
export function UserMenu() {
  const { name, isAuthenticated, readOnly, configured, signIn } = useAuthSession();
  const signOutFully = useSignOut();
  const [accountOpen, setAccountOpen] = useState(false);

  return (
    <>
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
              <>
                <MenuItem icon={<ContactCardRegular />} onClick={() => setAccountOpen(true)}>
                  My account
                </MenuItem>
                <MenuItem icon={<SignOutRegular />} onClick={signOutFully}>
                  Sign out
                </MenuItem>
              </>
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
      <AccountDialog open={accountOpen} onClose={() => setAccountOpen(false)} />
    </>
  );
}
