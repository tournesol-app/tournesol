import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';

import {
  BlankEnum,
  Recommendations_defaultDateEnum,
} from 'src/services/openapi';

interface RecommendationsDefaultDateProps {
  value: Recommendations_defaultDateEnum | BlankEnum;
  onChange: (target: Recommendations_defaultDateEnum | BlankEnum) => void;
}

const RecommendationsDefaultDate = ({
  value,
  onChange,
}: RecommendationsDefaultDateProps) => {
  const { t } = useTranslation();

  const settingChoices = [
    {
      label: t('filter.today'),
      value: 'TODAY',
    },
    {
      label: t('filter.thisWeek'),
      value: 'WEEK',
    },
    {
      label: t('filter.thisMonth'),
      value: 'MONTH',
    },
    {
      label: t('filter.thisYear'),
      value: 'YEAR',
    },
    {
      label: t('filter.allTime'),
      value: 'ALL_TIME',
    },
  ];

  return (
    <FormControl fullWidth>
      <InputLabel id="label__recommendations__default_date" color="secondary">
        {t('filter.uploadDate')}
      </InputLabel>
      <Select
        size="small"
        color="secondary"
        id="recommendations__default_date"
        labelId="label__recommendations__default_date"
        value={value}
        label={t('filter.uploadDate')}
        onChange={(event) =>
          onChange(
            event.target.value as Recommendations_defaultDateEnum | BlankEnum
          )
        }
      >
        {settingChoices.map((item) => (
          <MenuItem key={item.value} value={item.value}>
            {item.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default RecommendationsDefaultDate;
