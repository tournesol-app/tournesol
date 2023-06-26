import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';

import { Box, Button, Grid } from '@mui/material';
import { Save } from '@mui/icons-material';

import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useNotifications } from 'src/hooks';
import { theme } from 'src/theme';
import {
  ApiError,
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';
import {
  DEFAULT_RATE_LATER_AUTO_REMOVAL,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';

import { SettingsSection } from 'src/components';
import { subSectionBreakpoints } from 'src/pages/settings/layout';
import VideosPollUserSettingsForm from './VideosPollUserSettingsForm';

/**
 * Display a form allowing the logged users to update their general and the
 * `videos` poll preferences.
 */
const TournesolUserSettingsForm = () => {
  const pollName = YOUTUBE_POLL_NAME;

  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();

  const [disabled, setDisabled] = useState(false);
  const [apiErrors, setApiErrors] = useState<ApiError | null>(null);

  const userSettings = useSelector(selectSettings).settings;
  const pollSettings = userSettings?.videos;

  // Comparison
  const [displayedCriteria, setDisplayedCriteria] = useState<string[]>(
    pollSettings?.comparison__criteria_order ?? []
  );

  // Comparison (page)
  const [compUiWeeklyColGoalDisplay, setCompUiWeeklyColGoalDisplay] = useState<
    ComparisonUi_weeklyCollectiveGoalDisplayEnum | BlankEnum
  >(
    pollSettings?.comparison_ui__weekly_collective_goal_display ??
      ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS
  );

  // Rate-later settings
  const [rateLaterAutoRemoval, setRateLaterAutoRemoval] = useState(
    pollSettings?.rate_later__auto_remove ?? DEFAULT_RATE_LATER_AUTO_REMOVAL
  );

  // Recommendations (page)
  const [recoDefaultUnsafe, setRecoDefaultUnsafe] = useState(
    pollSettings?.recommendations__default_unsafe ?? false
  );
  const [recoDefaultUploadDate, setRecoDefaultUploadDate] = useState<
    Recommendations_defaultDateEnum | BlankEnum
  >(
    pollSettings?.recommendations__default_date ??
      Recommendations_defaultDateEnum.MONTH
  );

  useEffect(() => {
    if (!pollSettings) {
      return;
    }
    if (
      pollSettings.comparison_ui__weekly_collective_goal_display != undefined
    ) {
      setCompUiWeeklyColGoalDisplay(
        pollSettings.comparison_ui__weekly_collective_goal_display
      );
    }
    if (pollSettings?.comparison__criteria_order != undefined) {
      setDisplayedCriteria(pollSettings.comparison__criteria_order);
    }
    if (pollSettings.rate_later__auto_remove != undefined) {
      setRateLaterAutoRemoval(pollSettings.rate_later__auto_remove);
    }
    if (pollSettings.recommendations__default_unsafe != undefined) {
      setRecoDefaultUnsafe(pollSettings.recommendations__default_unsafe);
    }
    if (pollSettings.recommendations__default_date != undefined) {
      setRecoDefaultUploadDate(pollSettings.recommendations__default_date);
    }
  }, [pollSettings]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          [pollName]: {
            comparison__criteria_order: displayedCriteria,
            comparison_ui__weekly_collective_goal_display:
              compUiWeeklyColGoalDisplay,
            rate_later__auto_remove: rateLaterAutoRemoval,
            recommendations__default_date: recoDefaultUploadDate,
            recommendations__default_unsafe: recoDefaultUnsafe,
          },
        },
      }).catch((reason: ApiError) => {
        showErrorAlert(
          t('pollUserSettingsForm.errorOccurredDuringPreferencesUpdate')
        );

        setApiErrors(reason);
      });

    if (response) {
      showSuccessAlert(
        t('pollUserSettingsForm.preferencesUpdatedSuccessfully')
      );
      setApiErrors(null);
      dispatch(replaceSettings(response));
      (document.activeElement as HTMLElement).blur();
    }
    setDisabled(false);
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <SettingsSection
          title={`${t('preferences.preferencesRegarding')} ${t('poll.videos')}`}
          {...subSectionBreakpoints}
        >
          <VideosPollUserSettingsForm
            compUiWeeklyColGoalDisplay={compUiWeeklyColGoalDisplay}
            setCompUiWeeklyColGoalDisplay={setCompUiWeeklyColGoalDisplay}
            displayedCriteria={displayedCriteria}
            setDisplayedCriteria={setDisplayedCriteria}
            rateLaterAutoRemoval={rateLaterAutoRemoval}
            setRateLaterAutoRemoval={setRateLaterAutoRemoval}
            recoDefaultUnsafe={recoDefaultUnsafe}
            setRecoDefaultUnsafe={setRecoDefaultUnsafe}
            recoDefaultUploadDate={recoDefaultUploadDate}
            setRecoDefaultUploadDate={setRecoDefaultUploadDate}
            apiErrors={apiErrors}
          />
        </SettingsSection>
        <Box
          position="sticky"
          bottom={theme.spacing(2)}
          zIndex={theme.zIndex.fab}
          bgcolor="#fafafa"
        >
          <Grid position="sticky" {...subSectionBreakpoints}>
            <Button
              fullWidth
              type="submit"
              color="secondary"
              variant="contained"
              startIcon={<Save />}
              disabled={disabled}
            >
              {t('pollUserSettingsForm.updatePreferences')}
            </Button>
          </Grid>
        </Box>
      </form>
    </>
  );
};

export default TournesolUserSettingsForm;
