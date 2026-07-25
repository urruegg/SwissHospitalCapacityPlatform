import { Menu, MenuTrigger, MenuButton, MenuPopover, MenuList, MenuItemRadio } from '@fluentui/react-components';
import { BuildingRegular } from '@fluentui/react-icons';
import { useRoleLens } from '../../context/role-context';
import type { HospitalScope } from '../../auth/rbac-model';

/**
 * Sprint 20 M3 / Sprint 27 — hospital selector as an icon menu-button, scoped by
 * the active role lens. A single-site role renders a disabled button (the role
 * may only view its own site); an `aggregated` scope lists all sites.
 */
const SITES: HospitalScope[] = ['usz', 'luks', 'zollikerberg', 'aggregated'];

export function HospitalScopeSelector() {
  const { capabilities } = useRoleLens();
  const scope = capabilities.hospitalScope;
  const single = scope !== 'aggregated';
  const options: HospitalScope[] = single ? [scope] : SITES;
  return (
    <Menu checkedValues={{ hospital: [scope] }}>
      <MenuTrigger disableButtonEnhancement>
        <MenuButton aria-label="Hospital" icon={<BuildingRegular />} appearance="subtle" disabled={single}>
          {scope}
        </MenuButton>
      </MenuTrigger>
      <MenuPopover>
        <MenuList>
          {options.map((s) => (
            <MenuItemRadio key={s} name="hospital" value={s}>
              {s}
            </MenuItemRadio>
          ))}
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}
