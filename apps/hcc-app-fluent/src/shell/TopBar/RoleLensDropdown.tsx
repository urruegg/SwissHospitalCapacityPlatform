import { Menu, MenuTrigger, MenuButton, MenuPopover, MenuList, MenuItemRadio } from '@fluentui/react-components';
import { ShieldRegular } from '@fluentui/react-icons';
import { useRoleLens } from '../../context/role-context';
import type { HccRole } from '../../auth/rbac-model';

/**
 * Sprint 20 M3 / Sprint 27 — role lens as an icon menu-button.
 *
 * Lists ONLY the roles the user actually holds. Selecting narrows the active
 * access lens; `useRoleLens().setActiveRole` refuses to elevate beyond held
 * roles (design spec §7).
 */
export function RoleLensDropdown() {
  const { heldRoles, activeRole, setActiveRole } = useRoleLens();
  return (
    <Menu
      checkedValues={{ role: [activeRole] }}
      onCheckedValueChange={(_e, d) => {
        const next = d.checkedItems[0];
        if (next) setActiveRole(next as HccRole);
      }}
    >
      <MenuTrigger disableButtonEnhancement>
        <MenuButton aria-label="Role" icon={<ShieldRegular />} appearance="subtle">
          {activeRole}
        </MenuButton>
      </MenuTrigger>
      <MenuPopover>
        <MenuList>
          {heldRoles.map((r) => (
            <MenuItemRadio key={r} name="role" value={r}>
              {r}
            </MenuItemRadio>
          ))}
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}
