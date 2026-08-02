import {
  Dialog, DialogSurface, DialogTitle, DialogBody, DialogContent, DialogActions,
  Button, Badge, Divider, Text,
} from '@fluentui/react-components';
import { SignOutRegular } from '@fluentui/react-icons';
import { useAuthSession } from '../../auth/auth-session';
import { useSignOut } from '../../auth/use-sign-out';
import { useRoleLens } from '../../context/role-context';
import { getMsalTenantId } from '../../config/runtime-config';

/**
 * Sprint A (FR-AUTH-003) - My Account view. Read-only reflection of the signed-in
 * identity + the `HCC.*` roles claim: display name, UPN, oid, held roles, and the
 * active-role lens (scope + agent ceiling). No new data source - reuses the auth
 * session facade and the role lens. Sign out clears all per-user session context.
 */
export function AccountDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { name, username } = useAuthSession();
  const { userOid, heldRoles, activeRole, capabilities } = useRoleLens();
  const signOutFully = useSignOut();

  return (
    <Dialog open={open} onOpenChange={(_, d) => { if (!d.open) onClose(); }}>
      <DialogSurface aria-label="My account">
        <DialogBody>
          <DialogTitle>My account</DialogTitle>
          <DialogContent>
            <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 8, alignItems: 'center' }}>
              <Text weight="semibold">Name</Text><Text>{name}</Text>
              <Text weight="semibold">Sign-in</Text><Text>{username ?? '-'}</Text>
              <Text weight="semibold">Object id</Text><Text>{userOid ?? '-'}</Text>
              <Text weight="semibold">Tenant</Text><Text>{getMsalTenantId()}</Text>
            </div>
            <Divider style={{ margin: '12px 0' }}>Roles</Divider>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {heldRoles.map((r) => (
                <Badge key={r} appearance={r === activeRole ? 'filled' : 'tint'} color="brand">{r}</Badge>
              ))}
            </div>
            <Divider style={{ margin: '12px 0' }}>Active lens</Divider>
            <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: 8 }}>
              <Text weight="semibold">Active role</Text><Text>{activeRole}</Text>
              <Text weight="semibold">Hospital scope</Text><Text>{capabilities.hospitalScope}</Text>
              <Text weight="semibold">Agent ceiling</Text><Text>{capabilities.agentCeiling}</Text>
            </div>
          </DialogContent>
          <DialogActions>
            <Button appearance="secondary" onClick={onClose}>Close</Button>
            <Button appearance="primary" icon={<SignOutRegular />} onClick={signOutFully}>Sign out</Button>
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
}
