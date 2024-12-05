import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';

import { BlankEnum, FeedForyou_dateEnum } from 'src/services/openapi';

interface FeedForYouDateProps {
  scope: string;
  value: FeedForyou_dateEnum | BlankEnum;
  onChange: (target: FeedForyou_dateEnum | BlankEnum) => void;
}

const FeedForYouDate = ({ scope, value, onChange }: FeedForYouDateProps) => {
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
      <InputLabel id={`label_${scope}_feed_foryou__date`} color="secondary">
        {t('videosUserSettingsForm.feed.generic.uploadDate')}
      </InputLabel>
      <Select
        size="small"
        color="secondary"
        id={`${scope}_feed_foryou__date`}
        labelId={`label_${scope}_feed_foryou__date`}
        value={value}
        label={t('videosUserSettingsForm.recommendations.defaultUploadDate')}
        onChange={(event) =>
          onChange(event.target.value as FeedForyou_dateEnum | BlankEnum)
        }
        inputProps={{
          'data-testid': `${scope}_feed_foryou__date`,
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
