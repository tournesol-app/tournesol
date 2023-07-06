import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';

import { Notifications_langEnum } from 'src/services/openapi';

interface NotificationsLangProps {
  value: Notifications_langEnum;
  onChange: (lang: Notifications_langEnum) => void;
}

const NotificationsLang = ({ value, onChange }: NotificationsLangProps) => {
  const { t } = useTranslation();

  const settingChoices = [
    {
      label: t('language.en'),
      value: Notifications_langEnum.EN,
    },
    {
      label: t('language.fr'),
      value: Notifications_langEnum.FR,
    },
  ];

  return (
    <FormControl fullWidth>
      <InputLabel id="label__notifications__lang" color="secondary">
        {t('pollUserSettingsForm.preferredLanguage')}
      </InputLabel>
      <Select
        size="small"
        color="secondary"
        id="notifications__lang"
        labelId="label_notifications__lang"
        value={value}
        label={t('pollUserSettingsForm.preferredLanguage')}
        onChange={(event) =>
          onChange(event.target.value as Notifications_langEnum)
        }
        inputProps={{
          'data-testid': 'notifications__lang',
        }}
      >
        {settingChoices.map((item) => (
          <MenuItem key={item.value} value={item.value}>
            {item.label}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default NotificationsLang;
