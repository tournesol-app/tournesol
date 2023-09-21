import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface RecommendationsDefaultExcludeComparedProps {
  value: boolean;
  onChange: (target: boolean) => void;
  pollName: string;
}

const RecommendationsDefaultExcludeCompared = ({
  value,
  onChange,
  pollName,
}: RecommendationsDefaultExcludeComparedProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name={`${pollName}_recommendations__default_exclude_compared_entities`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${pollName}_recommendations__default_exclude_compared_entities`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('videosUserSettingsForm.recommendations.defaultExcludeCompared')}
    />
  );
};

export default RecommendationsDefaultExcludeCompared;
