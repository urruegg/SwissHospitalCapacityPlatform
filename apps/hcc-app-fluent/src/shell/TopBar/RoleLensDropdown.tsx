import { Dropdown, Option } from '@fluentui/react-components';
import { useRoleLens } from '../../context/role-context';
import type { HccRole } from '../../auth/rbac-model';

/**
 * Sprint 20 M3 — role lens dropdown.
 *
 * Lists ONLY the roles the user actually holds. Selecting narrows the active
 * access lens; `useRoleLens().setActiveRole` refuses to elevate beyond held
 * roles (design spec §7). Kept separate from the legacy `RoleSwitcher` so the
 * legacy top bar (removed in M4) keeps its own behaviour until then.
 */
export function RoleLensDropdown() {
  const { heldRoles, activeRole, setActiveRole } = useRoleLens();
  return (
    <Dropdown
      aria-label="Role"
      value={activeRole}
      selectedOptions={[activeRole]}
      onOptionSelect={(_e, d) => {
        if (d.optionValue) setActiveRole(d.optionValue as HccRole);
      }}
    >
      {heldRoles.map((r) => (
        <Option key={r} value={r}>
          {r}
        </Option>
      ))}
    </Dropdown>
  );
}
