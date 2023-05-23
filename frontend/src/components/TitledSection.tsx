import React, { useState } from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { Save } from '@mui/icons-material';
import {
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';
import { useNotifications } from 'src/hooks';
import { useTranslation } from 'react-i18next';
import { replaceSettings } from 'src/features/settings/userSettingsSlice';
import { useDispatch } from 'react-redux';

interface Props {
  title: string;
  children: React.ReactNode;
  canSave?: boolean;
  value?: string;
}

const getDateTranslation = (value: string) => {
  switch (value) {
    case 'Today':
      return Recommendations_defaultDateEnum.TODAY;
    case 'Week':
      return Recommendations_defaultDateEnum.WEEK;
    case 'Month':
      return Recommendations_defaultDateEnum.MONTH;
    case 'Year':
      return Recommendations_defaultDateEnum.YEAR;
    default:
      return Recommendations_defaultDateEnum.ALL_TIME;
  }
};

const TitledSection = ({ title, children, canSave = false, value }: Props) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();

  const [disabled, setDisabled] = useState(false);

  const settingToUpdate = () => {
    if (title === t('filter.uploadDate'))
      return { recommendations__default_date: getDateTranslation(value || '') };
    else if (title === t('filter.advanced'))
      return {
        recommendations__default_unsafe: value === 'true' ? true : false,
      };
    else return {};
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          [YOUTUBE_POLL_NAME]: settingToUpdate(),
        },
      }).catch(() => {
        showErrorAlert(
          t('pollUserSettingsForm.errorOccurredDuringPreferencesUpdate')
        );
      });

    if (response) {
      showSuccessAlert(
        t('pollUserSettingsForm.preferencesUpdatedSuccessfully')
      );
      dispatch(replaceSettings(response));
      (document.activeElement as HTMLElement).blur();
    }

    setDisabled(false);
  };

  return (
    <>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Typography
          variant="h6"
          sx={{
            borderBottom: '1px solid #E7E5DB',
            marginBottom: '0.3em',
          }}
          style={{ flexGrow: 1, flexShrink: 0 }}
        >
          {title}
        </Typography>
        {canSave ? (
          <IconButton onClick={handleSubmit} disabled={disabled}>
            <Save />
          </IconButton>
        ) : null}
      </Box>
      {children}
    </>
  );
};

export default TitledSection;
