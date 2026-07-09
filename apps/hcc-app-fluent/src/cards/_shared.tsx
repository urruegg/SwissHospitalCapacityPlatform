import { makeStyles, tokens, Card, CardHeader, Body1, Caption1 } from '@fluentui/react-components';
import type { ReactNode } from 'react';

const useStyles = makeStyles({
  card: {
    width: '260px',
    padding: tokens.spacingHorizontalM,
    boxShadow: tokens.shadow8,
  },
});

/** Sprint 13 T3 — common card chrome so each card type stays small and focused. */
export function CardShell({
  title,
  subtitle,
  children,
  accent,
  testId,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  accent?: string;
  testId: string;
}) {
  const styles = useStyles();
  return (
    <Card className={styles.card} data-card-type={testId} appearance="filled">
      <CardHeader
        header={<Body1 style={{ color: accent }}><b>{title}</b></Body1>}
        description={subtitle ? <Caption1>{subtitle}</Caption1> : undefined}
      />
      {children}
    </Card>
  );
}
