import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface AutoSelectoEntitiesProps {
  value: boolean;
  onChange: (target: boolean) => void;
  pollName: string;
}

const AutoSelectoEntities = ({
  value,
  onChange,
  pollName,
}: AutoSelectoEntitiesProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name={`${pollName}_comparison__auto_select_entities`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `${pollName}_comparison__auto_select_entities`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('pollUserSettingsForm.letTournesolSuggestElements')}
    />
  );
};

export default AutoSelectoEntities;
