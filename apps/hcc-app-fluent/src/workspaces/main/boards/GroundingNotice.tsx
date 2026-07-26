import { MessageBar, MessageBarBody, MessageBarTitle } from '@fluentui/react-components';

/**
 * Sprint 27 — fail-loud grounding notice. Rendered when an IQ structured read
 * was configured but unavailable and the data layer fell back to a simulated
 * fixture (`RoleBoardData.degraded`). Never render golden figures silently when
 * the golden source is down — surface the degradation.
 */
export function GroundingNotice({ degraded }: { degraded?: boolean }) {
  if (!degraded) return null;
  return (
    <MessageBar intent="warning" data-testid="grounding-degraded">
      <MessageBarBody>
        <MessageBarTitle>Grounding degraded</MessageBarTitle>{' '}
        The IQ layer was unavailable — showing simulated data. Figures are not live golden evidence.
      </MessageBarBody>
    </MessageBar>
  );
}
