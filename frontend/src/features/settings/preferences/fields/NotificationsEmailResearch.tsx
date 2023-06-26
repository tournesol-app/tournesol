import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControlLabel, Switch } from '@mui/material';

interface RecommendationsDefaultUnsafeProps {
  value: boolean;
  onChange: (target: boolean) => void;
}

const NotificationsEmailResearch = ({
  value,
  onChange,
}: RecommendationsDefaultUnsafeProps) => {
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
        />
      }
      label={t('generalUserSettings.notificationsEmailResearch')}
    />
  );
};

export default NotificationsEmailResearch;
