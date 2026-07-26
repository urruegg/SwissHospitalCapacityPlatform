import { Menu, MenuTrigger, MenuButton, MenuPopover, MenuList, MenuItemRadio } from '@fluentui/react-components';
import { BuildingRegular } from '@fluentui/react-icons';
import { useRoleLens } from '../../context/role-context';
import { useHospital } from '../../context/hospital-context';
import type { Hospital } from '../../auth/claim-parser';
import { HOSPITAL_OPTIONS, orgForScope } from '../../data/reference/organizations';

/**
 * Sprint 20 M3 / Sprint 27 — hospital selector, sourced from the Entra
 * organizations master data (`data/entra/organizations.csv` via
 * `data/reference/organizations`). Options are the real hospital scopes; a
 * single-site role lens locks to its own site (disabled), an aggregated lens can
 * switch. Selecting sets the active hospital, which re-scopes the boards.
 */
export function HospitalScopeSelector() {
  const { capabilities } = useRoleLens();
  const { hospital, setHospital } = useHospital();
  const roleScope = capabilities.hospitalScope;
  const locked = roleScope !== 'aggregated';
  const current: Hospital = locked ? (roleScope as Hospital) : hospital;
  const options = locked ? HOSPITAL_OPTIONS.filter((o) => o.scopeId === current) : HOSPITAL_OPTIONS;
  const label = orgForScope(current)?.shortName ?? current;
  return (
    <Menu
      checkedValues={{ hospital: [current] }}
      onCheckedValueChange={(_e, d) => {
        const next = d.checkedItems[0];
        if (next) setHospital(next as Hospital);
      }}
    >
      <MenuTrigger disableButtonEnhancement>
        <MenuButton aria-label="Hospital" icon={<BuildingRegular />} appearance="subtle" disabled={locked}>
          {label}
        </MenuButton>
      </MenuTrigger>
      <MenuPopover>
        <MenuList>
          {options.map((o) => (
            <MenuItemRadio key={o.scopeId} name="hospital" value={o.scopeId}>
              {o.displayName}
            </MenuItemRadio>
          ))}
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}
