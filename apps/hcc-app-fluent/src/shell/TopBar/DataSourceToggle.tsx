import { Switch } from '@fluentui/react-components';
import { useDataSource } from '../../context/data-source-context';

/**
 * Sprint 27 — header toggle switching board data between live golden evidence
 * (IQ layer) and simulated fixtures. When `live` is selected but no golden source
 * is configured, boards fail loud (GroundingNotice) rather than faking live data.
 */
export function DataSourceToggle() {
  const { source, setSource } = useDataSource();
  return (
    <Switch
      aria-label="Data source"
      checked={source === 'live'}
      label={source === 'live' ? 'Live' : 'Simulated'}
      onChange={(_e, d) => setSource(d.checked ? 'live' : 'simulated')}
    />
  );
}
