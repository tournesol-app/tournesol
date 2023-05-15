import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';

import { Button, Grid, Typography } from '@mui/material';

import {
  DEFAULT_RATE_LATER_AUTO_REMOVAL,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useNotifications } from 'src/hooks';
import {
  ApiError,
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';
import RateLaterAutoRemoveField from './fields/RateLaterAutoRemove';
import WeeklyCollectiveGoalDisplayField from './fields/WeeklyCollectiveGoalDisplay';
import RecommendationsDefaultUnsafe from './fields/RecommendationsDefaultUnsafe';
import RecommendationsDefaultDate from './fields/RecommendationsDefaultDate';
import RecommendationsDefaultLanguage from './fields/RecommendationsDefaultLanguage';

/**
 * Display a generic user settings form that can be used by any poll.
 */
const VideosPollUserSettingsForm = () => {
  const pollName = YOUTUBE_POLL_NAME;

  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();

  const [disabled, setDisabled] = useState(false);
  const [apiErrors, setApiErrors] = useState<ApiError | null>(null);

  // List of user's settings.
  const userSettings = useSelector(selectSettings).settings;

  // Comparison (page)
  const [compUiWeeklyColGoalDisplay, setCompUiWeeklyColGoalDisplay] = useState<
    ComparisonUi_weeklyCollectiveGoalDisplayEnum | BlankEnum
  >(
    userSettings?.[pollName]?.comparison_ui__weekly_collective_goal_display ??
      ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS
  );

  // Rate-later settings
  const [rateLaterAutoRemoval, setRateLaterAutoRemoval] = useState(
    userSettings?.[pollName]?.rate_later__auto_remove ??
      DEFAULT_RATE_LATER_AUTO_REMOVAL
  );

  // Recommendations (page)
  const [unsafe, setUnsafe] = useState(
    userSettings?.[pollName]?.recommendations__default_unsafe ?? false
  );
  const [date, setDate] = useState(
    userSettings?.[pollName]?.recommendations__default_date ??
      Recommendations_defaultDateEnum.MONTH
  );
  const [language, setLanguage] = useState(
    userSettings?.[pollName]?.recommendations__default_language ?? ['en', 'fr']
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          [pollName]: {
            comparison_ui__weekly_collective_goal_display:
              compUiWeeklyColGoalDisplay,
            rate_later__auto_remove: rateLaterAutoRemoval,
            recommendations__default_unsafe: unsafe,
            recommendations__default_date: date,
            recommendations__default_language: language,
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
    <form onSubmit={handleSubmit}>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <Grid item>
          <Typography variant="h6">
            {t('pollUserSettingsForm.comparisonPage')}
          </Typography>
        </Grid>
        <Grid item>
          <WeeklyCollectiveGoalDisplayField
            value={compUiWeeklyColGoalDisplay}
            onChange={setCompUiWeeklyColGoalDisplay}
            pollName={pollName}
          />
        </Grid>
        <Grid item>
          <Typography variant="h6">
            {t('pollUserSettingsForm.rateLater')}
          </Typography>
        </Grid>
        <Grid item>
          <RateLaterAutoRemoveField
            apiErrors={apiErrors}
            value={rateLaterAutoRemoval}
            onChange={setRateLaterAutoRemoval}
            pollName={pollName}
          />
        </Grid>
        <Grid item>
          <Typography variant="h6">
            {t('pollUserSettingsForm.recommendationsPage')}
          </Typography>
        </Grid>
        <Grid item>
          <RecommendationsDefaultUnsafe value={unsafe} onChange={setUnsafe} />
        </Grid>
        <Grid item>
          <RecommendationsDefaultDate value={date} onChange={setDate} />
        </Grid>
        <Grid item>
          <RecommendationsDefaultLanguage
            value={language}
            onChange={setLanguage}
          />
        </Grid>
        <Grid item>
          <Button
            fullWidth
            type="submit"
            color="secondary"
            variant="contained"
            disabled={disabled}
          >
            {t('pollUserSettingsForm.updatePreferences')}
          </Button>
        </Grid>
      </Grid>
    </form>
  );
};

export default VideosPollUserSettingsForm;
