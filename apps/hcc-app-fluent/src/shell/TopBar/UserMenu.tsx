import { Menu, MenuTrigger, MenuPopover, MenuList, MenuItem, Button } from '@fluentui/react-components';
import { PersonRegular } from '@fluentui/react-icons';

/** Sprint 20 M3 — user menu (login/logout entry point). */
export function UserMenu({ name = 'Demo User' }: { name?: string }) {
  return (
    <Menu>
      <MenuTrigger disableButtonEnhancement>
        <Button aria-label="User menu" icon={<PersonRegular />} appearance="subtle">
          {name}
        </Button>
      </MenuTrigger>
      <MenuPopover>
        <MenuList>
          <MenuItem>Sign out</MenuItem>
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}
