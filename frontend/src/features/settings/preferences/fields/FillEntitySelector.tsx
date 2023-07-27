import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface FillEntitySelectorProps {
  value: boolean;
  onChange: (target: boolean) => void;
  pollName: string;
}

const FillEntitySelector = ({
  value,
  onChange,
  pollName,
}: FillEntitySelectorProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name={`${pollName}_comparison__fill_entity_selector`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${pollName}_comparison__fill_entity_selector`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('pollUserSettingsForm.letTournesolLoadVideos')}
    />
  );
};

export default FillEntitySelector;
