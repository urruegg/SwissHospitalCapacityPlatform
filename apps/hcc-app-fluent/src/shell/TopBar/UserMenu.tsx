import { Menu, MenuTrigger, MenuPopover, MenuList, MenuItem, Button } from '@fluentui/react-components';
import { PersonRegular } from '@fluentui/react-icons';
import { resetConversations } from '../../copilot-drawer/conversation-store';

/** Sprint 20 M3 — user menu (login/logout entry point). */
export function UserMenu({ name = 'Demo User' }: { name?: string }) {
  // Sprint 29 M1 — clear every (user x agent) conversation thread on sign-out
  // so a subsequent session never inherits a prior user's chat context.
  return (
    <Menu>
      <MenuTrigger disableButtonEnhancement>
        <Button aria-label="User menu" icon={<PersonRegular />} appearance="subtle">
          {name}
        </Button>
      </MenuTrigger>
      <MenuPopover>
        <MenuList>
          <MenuItem onClick={() => resetConversations()}>Sign out</MenuItem>
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}
