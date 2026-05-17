import React from 'react';
import { useTranslation } from 'react-i18next';

import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';

import { BlankEnum, Extension_onVideoWatchedEnum } from 'src/services/openapi';

interface ExtOnVideoWatchedProps {
  value: Extension_onVideoWatchedEnum | BlankEnum;
  onChange: (target: Extension_onVideoWatchedEnum | BlankEnum) => void;
  pollName: string;
}

const ExtOnVideoWatched = ({
  value,
  onChange,
  pollName,
}: ExtOnVideoWatchedProps) => {
  const { t } = useTranslation();

  const settingChoices = [
    {
      label: t('pollUserSettingsForm.onVideoWatchedDoNothing'),
      value: Extension_onVideoWatchedEnum.DO_NOTHING,
    },
    {
      label: t('pollUserSettingsForm.onVideoWatchedMarkAsWatched'),
      value: Extension_onVideoWatchedEnum.MARK_AS_WATCHED,
    },
  ];

  return (
    <FormControl fullWidth>
      <InputLabel
        id={`label_${pollName}_extension__on_video_watched`}
        color="secondary"
      >
        {t('pollUserSettingsForm.whenAVideoIsWatchedOnYouTube')}
      </InputLabel>
      <Select
        size="small"
        color="secondary"
        id={`${pollName}_extension__on_video_watched`}
        labelId={`label_${pollName}_extension__on_video_watched`}
        value={value}
        label={t('pollUserSettingsForm.whenAVideoIsWatchedOnYouTube')}
        onChange={(event) =>
          onChange(
            event.target.value as Extension_onVideoWatchedEnum | BlankEnum
          )
        }
        inputProps={{
          'data-testid': `${pollName}_extension__on_video_watched`,
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

export default ExtOnVideoWatched;
