import React, { useEffect, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';

import {
  Alert,
  Button,
  Fab,
  Grid,
  Typography,
  Zoom,
  useMediaQuery,
} from '@mui/material';
import { Save } from '@mui/icons-material';

import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useNotifications, useScrollToLocation } from 'src/hooks';
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

import ComparisonOptionalCriteriaDisplayed from './fields/ComparisonOptionalCriteriaDisplayed';
import RateLaterAutoRemoveField from './fields/RateLaterAutoRemove';
import WeeklyCollectiveGoalDisplayField from './fields/WeeklyCollectiveGoalDisplay';
import RecommendationsDefaultUnsafe from './fields/RecommendationsDefaultUnsafe';
import RecommendationsDefaultDate from './fields/RecommendationsDefaultDate';

/**
 * Display a form allowing the logged users to update their preferences for
 * the `videos` poll.
 */
const VideosPollUserSettingsForm = () => {
  const pollName = YOUTUBE_POLL_NAME;

  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();
  const mediaBelowSm = useMediaQuery(theme.breakpoints.down('sm'));

  const [disabled, setDisabled] = useState(false);
  const [apiErrors, setApiErrors] = useState<ApiError | null>(null);

  const [displayFab, setDisplayFab] = useState(true);

  useScrollToLocation();

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
    const toggleFab = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setDisplayFab(false);
        } else {
          setDisplayFab(true);
        }
      });
    };

    const options = { threshold: 0.94 };
    const observer = new IntersectionObserver(toggleFab, options);

    const target = document.querySelector('#preferences-main-submit');
    if (target) {
      observer.observe(target);
    }

    return () => observer.disconnect();
  }, []);

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
    <form onSubmit={handleSubmit}>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <Grid item>
          <Typography id="comparison_page" variant="h6">
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
        {/*
          Ideally the following field could be displayed under the title
          Comparison, instead of Comparison (page). Updating the optinal
          criteria displayed by default will affect all comparison UIs and not
          just the comparison page. When an another user setting will be added
          to customize the comparisons (not the page), consider the creation of
          a section Comparison.
        */}
        <Grid item>
          <ComparisonOptionalCriteriaDisplayed
            displayedCriteria={displayedCriteria}
            onChange={setDisplayedCriteria}
          />
        </Grid>
        <Grid item>
          <Typography id="rate_later" variant="h6">
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
          <Typography id="recommendations_page" variant="h6">
            {t('pollUserSettingsForm.recommendationsPage')}
          </Typography>
        </Grid>
        <Grid item>
          <Alert severity="info">
            <Trans
              t={t}
              i18nKey="pollUserSettingsForm.customizeYourDefaultSearchFilter"
            >
              Customize <strong>the default search filters</strong> according to
              your own preferences. Those filters are applied{' '}
              <strong>only</strong> when you access the recommendations from the{' '}
              <strong>main menu</strong>.
            </Trans>
          </Alert>
        </Grid>
        <Grid item>
          <RecommendationsDefaultDate
            value={recoDefaultUploadDate}
            onChange={setRecoDefaultUploadDate}
            pollName={pollName}
          />
        </Grid>
        <Grid item>
          <RecommendationsDefaultUnsafe
            value={recoDefaultUnsafe}
            onChange={setRecoDefaultUnsafe}
            pollName={pollName}
          />
        </Grid>
        <Grid item>
          <Button
            id="preferences-main-submit"
            data-testid="preferences-main-submit"
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

      <Zoom in={displayFab} unmountOnExit={true}>
        <Fab
          color="primary"
          type="submit"
          disabled={disabled}
          aria-label={t('pollUserSettingsForm.updatePreferencesAltButton')}
          data-testid="preferences-alt-submit"
          sx={{
            position: 'fixed',
            right: theme.spacing(mediaBelowSm ? 2 : 4),
            bottom: theme.spacing(mediaBelowSm ? 2 : 4),
          }}
        >
          <Save />
        </Fab>
      </Zoom>
    </form>
  );
};

export default VideosPollUserSettingsForm;
