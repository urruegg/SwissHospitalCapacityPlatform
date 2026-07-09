import { Dropdown, Option } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useHospital } from '../../context/hospital-context';
import type { Hospital } from '../../auth/claim-parser';

const HOSPITALS: Hospital[] = ['usz', 'luks', 'zollikerberg', 'aggregated'];

/** Sprint 13 T4 — hospital-context selector (USZ / LUKS / Zollikerberg / Aggregated). */
export function HospitalSelector() {
  const { t } = useTranslation();
  const { hospital, setHospital } = useHospital();
  return (
    <Dropdown
      aria-label={t('topbar.hospital')}
      value={t(`hospitals.${hospital}`)}
      selectedOptions={[hospital]}
      onOptionSelect={(_e, data) => {
        if (data.optionValue) setHospital(data.optionValue as Hospital);
      }}
    >
      {HOSPITALS.map((h) => (
        <Option key={h} value={h}>
          {t(`hospitals.${h}`)}
        </Option>
      ))}
    </Dropdown>
  );
}
