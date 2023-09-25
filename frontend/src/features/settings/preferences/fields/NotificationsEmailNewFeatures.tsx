import React from 'react';
import { useTranslation } from 'react-i18next';

import BooleanField from './generics/BooleanField';

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
    <BooleanField
      scope="general"
      name="notifications_email__new_features"
      label={t('generalUserSettingsForm.notificationsEmailNewFeatures')}
      value={value}
      onChange={onChange}
    />
  );
};

export default NotificationsEmailNewFeatures;
