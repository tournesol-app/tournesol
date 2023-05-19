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
  pollName: string;
}

const RecommendationsDefaultDate = ({
  value,
  onChange,
  pollName,
}: RecommendationsDefaultDateProps) => {
  const { t } = useTranslation();

  const settingChoices = [
    {
      label: t('filter.today'),
      value: Recommendations_defaultDateEnum.TODAY,
    },
    {
      label: t('filter.thisWeek'),
      value: Recommendations_defaultDateEnum.WEEK,
    },
    {
      label: t('filter.thisMonth'),
      value: Recommendations_defaultDateEnum.MONTH,
    },
    {
      label: t('filter.thisYear'),
      value: Recommendations_defaultDateEnum.YEAR,
    },
    {
      label: t('filter.allTime'),
      value: Recommendations_defaultDateEnum.ALL_TIME,
    },
  ];

  return (
    <FormControl fullWidth>
      <InputLabel
        id={`label_${pollName}_recommendations__default_date`}
        color="secondary"
      >
        {t('videosUserSettingsForm.recommendations.defaultUploadDate')}
      </InputLabel>
      <Select
        size="small"
        color="secondary"
        id={`${pollName}_recommendations__default_date`}
        labelId={`label_${pollName}_recommendations__default_date`}
        value={value}
        label={t('videosUserSettingsForm.recommendations.defaultUploadDate')}
        onChange={(event) =>
          onChange(
            event.target.value as Recommendations_defaultDateEnum | BlankEnum
          )
        }
        inputProps={{
          'data-testid': `${pollName}_recommendations__default_date`,
        }}
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
