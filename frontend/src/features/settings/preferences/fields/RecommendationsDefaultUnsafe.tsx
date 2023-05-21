import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface RecommendationsDefaultUnsafeProps {
  value: boolean;
  onChange: (target: boolean) => void;
  pollName: string;
}

const RecommendationsDefaultUnsafe = ({
  value,
  onChange,
  pollName,
}: RecommendationsDefaultUnsafeProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name={`${pollName}_recommendations__default_unsafe`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${pollName}_recommendations__default_unsafe`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('videosUserSettingsForm.recommendations.defaultUnsafe')}
    />
  );
};

export default RecommendationsDefaultUnsafe;
