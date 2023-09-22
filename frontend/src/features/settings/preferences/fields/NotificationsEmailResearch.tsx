import React from 'react';
import { useTranslation } from 'react-i18next';

import BooleanField from './generics/BooleanField';

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
    <BooleanField
      scope="general"
      name="notifications_email__research"
      label={t('generalUserSettingsForm.notificationsEmailResearch')}
      value={value}
      onChange={onChange}
    />
  );
};

export default NotificationsEmailResearch;
