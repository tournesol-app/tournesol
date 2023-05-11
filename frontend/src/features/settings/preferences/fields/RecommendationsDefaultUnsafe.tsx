import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface RecommendationsDefaultUnsafeProps {
  value: boolean;
  onChange: (target: boolean) => void;
}

const RecommendationsDefaultUnsafe = ({
  value,
  onChange,
}: RecommendationsDefaultUnsafeProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          edge="start"
        />
      }
      label={t('pollUserSettingsForm.defaultUnsafe')}
    />
  );
};

export default RecommendationsDefaultUnsafe;
