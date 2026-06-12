import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';

import { Box, Button, Paper, Stack, Typography } from '@mui/material';
import { Save } from '@mui/icons-material';

import ExtOnVideoWatched from 'src/features/settings/preferences/fields/ExtOnVideoWatched';
import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useNotifications } from 'src/hooks';
import {
  ApiError,
  BlankEnum,
  Extension_onVideoWatchedEnum,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';
import {
  YOUTUBE_POLL_NAME,
  YT_DEFAULT_EXTENSION_ON_VIDEO_WATHCED,
} from 'src/utils/constants';

const RateLaterOnVideoWatchedSetting = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();

  const pollSettings = useSelector(selectSettings).settings?.videos;

  const [onVideoWatchedSetting, setOnVideoWatchedSetting] = useState<
    Extension_onVideoWatchedEnum | BlankEnum
  >(
    pollSettings?.extension__on_video_watched ??
      YT_DEFAULT_EXTENSION_ON_VIDEO_WATHCED
  );
  const [disabled, setDisabled] = useState(false);

  useEffect(() => {
    if (pollSettings?.extension__on_video_watched != undefined) {
      setOnVideoWatchedSetting(pollSettings.extension__on_video_watched);
    }
  }, [pollSettings?.extension__on_video_watched]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          [YOUTUBE_POLL_NAME]: {
            extension__on_video_watched: onVideoWatchedSetting,
          },
        },
      }).catch((reason: ApiError) => {
        showErrorAlert(
          t('pollUserSettingsForm.errorOccurredDuringPreferencesUpdate')
        );
        console.error(reason);
      });

    if (response) {
      showSuccessAlert(
        t('pollUserSettingsForm.preferencesUpdatedSuccessfully')
      );
      dispatch(replaceSettings(response));
    }

    setDisabled(false);
  };

  return (
    <Paper sx={{ p: 2, width: '100%' }}>
      <Box component="form" onSubmit={handleSubmit}>
        <Typography sx={{ mb: 2 }}>
          {t('ratelater.extensionInstalledChooseOnVideoWatched')}
        </Typography>
        <ExtOnVideoWatched
          value={onVideoWatchedSetting}
          onChange={setOnVideoWatchedSetting}
          pollName={YOUTUBE_POLL_NAME}
        />
        <Stack direction="row" sx={{ justifyContent: 'flex-end', mt: 2 }}>
          <Button
            type="submit"
            size="small"
            color="secondary"
            variant="contained"
            startIcon={<Save />}
            disabled={disabled}
          >
            {t('pollUserSettingsForm.updatePreferences')}
          </Button>
        </Stack>
      </Box>
    </Paper>
  );
};

export default RateLaterOnVideoWatchedSetting;
