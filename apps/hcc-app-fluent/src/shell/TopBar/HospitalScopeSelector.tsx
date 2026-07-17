import { Dropdown, Option } from '@fluentui/react-components';
import { useRoleLens } from '../../context/role-context';
import type { HospitalScope } from '../../auth/rbac-model';

/**
 * Sprint 20 M3 — hospital selector scoped by the active role lens.
 *
 * When the active role's `hospitalScope` resolves to a single site the control
 * is a disabled, single-value dropdown (the role may only view its own site).
 * When the scope is `aggregated` the user may pick any site or the aggregated
 * view (design spec §7 RBAC lens).
 */
const SITES: HospitalScope[] = ['usz', 'luks', 'zollikerberg', 'aggregated'];

export function HospitalScopeSelector() {
  const { capabilities } = useRoleLens();
  const scope = capabilities.hospitalScope;
  const single = scope !== 'aggregated';
  const options: HospitalScope[] = single ? [scope] : SITES;
  return (
    <Dropdown
      aria-label="Hospital"
      disabled={single}
      value={scope}
      selectedOptions={[scope]}
    >
      {options.map((s) => (
        <Option key={s} value={s}>
          {s}
        </Option>
      ))}
    </Dropdown>
  );
}
