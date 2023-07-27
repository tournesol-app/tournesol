import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface FillEntitySelectorAutoProps {
  value: boolean;
  onChange: (target: boolean) => void;
  pollName: string;
}

const FillEntitySelectorAuto = ({
  value,
  onChange,
  pollName,
}: FillEntitySelectorAutoProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name={`${pollName}_comparison__entity_selector_auto`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${pollName}_comparison__entity_selector_auto`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('pollUserSettingsForm.letTournesolLoadVideos')}
    />
  );
};

export default FillEntitySelectorAuto;
