import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';

import { BlankEnum, FeedForyou_dateEnum } from 'src/services/openapi';

interface FeedForYouDateProps {
  value: FeedForyou_dateEnum | BlankEnum;
  onChange: (target: FeedForyou_dateEnum | BlankEnum) => void;
  pollName: string;
}

const FeedForYouDate = ({ value, onChange, pollName }: FeedForYouDateProps) => {
  const { t } = useTranslation();

  const settingChoices = [
    {
      label: t('filter.today'),
      value: FeedForyou_dateEnum.TODAY,
    },
    {
      label: t('filter.thisWeek'),
      value: FeedForyou_dateEnum.WEEK,
    },
    {
      label: t('filter.thisMonth'),
      value: FeedForyou_dateEnum.MONTH,
    },
    {
      label: t('filter.thisYear'),
      value: FeedForyou_dateEnum.YEAR,
    },
    {
      label: t('filter.allTime'),
      value: FeedForyou_dateEnum.ALL_TIME,
    },
  ];

  return (
    <FormControl fullWidth>
      <InputLabel
        id={`label_${pollName}_feed_foryou__default_date`}
        color="secondary"
      >
        {t('videosUserSettingsForm.foryou.uploadDate')}
      </InputLabel>
      <Select
        size="small"
        color="secondary"
        id={`${pollName}_feed_foryou__default_date`}
        labelId={`label_${pollName}_feed_foryou__default_date`}
        value={value}
        label={t('videosUserSettingsForm.recommendations.defaultUploadDate')}
        onChange={(event) =>
          onChange(event.target.value as FeedForyou_dateEnum | BlankEnum)
        }
        inputProps={{
          'data-testid': `${pollName}_feed_foryou__default_date`,
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

export default FeedForYouDate;
