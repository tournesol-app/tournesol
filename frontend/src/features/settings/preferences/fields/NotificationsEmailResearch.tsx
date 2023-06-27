import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface NotificationsEmailResearchProps {
  value: boolean;
  onChange: (target: boolean) => void;
}

const NotificationsEmailResearch = ({
  value,
  onChange,
}: NotificationsEmailResearchProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name={`notifications_email__research`}
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `notifications_email__research`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('generalUserSettings.notificationsEmailResearch')}
    />
  );
};

export default NotificationsEmailResearch;
