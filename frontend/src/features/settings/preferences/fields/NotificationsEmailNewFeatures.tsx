import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface NotificationsEmailNewFeaturesProps {
  value: boolean;
  onChange: (target: boolean) => void;
}

const NotificationsEmailNewFeatures = ({
  value,
  onChange,
}: NotificationsEmailNewFeaturesProps) => {
  const { t } = useTranslation();

  return (
    <FormControlLabel
      control={
        <Switch
          name="notifications_email__new_features"
          checked={value}
          onChange={() => onChange(!value)}
          size="medium"
          color="secondary"
          inputProps={
            {
              'data-testid': `notifications_email__new_features`,
            } as React.InputHTMLAttributes<HTMLInputElement>
          }
        />
      }
      label={t('generalUserSettingsForm.notificationsEmailNewFeatures')}
    />
  );
};

export default NotificationsEmailNewFeatures;
