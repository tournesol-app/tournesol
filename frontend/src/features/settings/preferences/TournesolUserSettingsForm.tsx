import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';

import { Box, Button, Grid } from '@mui/material';
import { Save } from '@mui/icons-material';

import { SettingsSection } from 'src/components';
import {
  replaceSettings,
  selectSettings,
} from 'src/features/settings/userSettingsSlice';
import { useNotifications, useScrollToLocation } from 'src/hooks';
import { theme } from 'src/theme';
import {
  mainSectionGridSpacing,
  subSectionBreakpoints,
} from 'src/pages/settings/layout';
import {
  ApiError,
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  Notifications_langEnum,
  Recommendations_defaultDateEnum,
  TournesolUserSettings,
  UsersService,
} from 'src/services/openapi';
import {
  DEFAULT_RATE_LATER_AUTO_REMOVAL,
  YOUTUBE_POLL_NAME,
  YT_DEFAULT_AUTO_SELECT_ENTITIES,
  YT_DEFAULT_UI_WEEKLY_COL_GOAL_MOBILE,
} from 'src/utils/constants';
import {
  initRecommendationsLanguages,
  saveRecommendationsLanguages,
} from 'src/utils/recommendationsLanguages';

import GeneralUserSettingsForm from './GeneralUserSettingsForm';
import VideosPollUserSettingsForm from './VideosPollUserSettingsForm';

const initialLanguages = () => {
  const languages = initRecommendationsLanguages();
  return languages ? languages.split(',') : [];
};

/**
 * Display a form allowing the logged users to update all their Tournesol
 * preferences.
 */
const TournesolUserSettingsForm = () => {
  const { t } = useTranslation();

  const dispatch = useDispatch();
  const { showSuccessAlert, showErrorAlert } = useNotifications();

  const [disabled, setDisabled] = useState(false);
  const [apiErrors, setApiErrors] = useState<ApiError | null>(null);

  const userSettings = useSelector(selectSettings).settings;
  const generalSettings = userSettings?.general;
  const pollSettings = userSettings?.videos;

  useScrollToLocation();

  /**
   * General user settings
   */

  // We think that the majority of the community speaks french.
  const [notificationsLang, setNotificationsLang] = useState(
    generalSettings?.notifications__lang ?? Notifications_langEnum.FR
  );

  // Notifications (must be false by default according to the ToS)
  const [notificationsEmailResearch, setNotificationsEmailResearch] = useState(
    generalSettings?.notifications_email__research ?? false
  );

  const [notificationsEmailNewFeatures, setNotificationsEmailNewFeatures] =
    useState(generalSettings?.notifications_email__new_features ?? false);

  /**
   * Poll `videos`
   */

  // Browser extension
  const [extSearchRecommendation, setExtSearchRecommendation] = useState(
    pollSettings?.extension__search_reco ?? false
  );

  // Comparison
  const [autoSelectEntities, setAutoSelectEntities] = useState(
    pollSettings?.comparison__auto_select_entities ??
      YT_DEFAULT_AUTO_SELECT_ENTITIES
  );

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

  const [compUiWeeklyColGoalMobile, setCompUiWeeklyColGoalMobile] = useState(
    pollSettings?.comparison_ui__weekly_collective_goal_mobile ??
      YT_DEFAULT_UI_WEEKLY_COL_GOAL_MOBILE
  );

  // Rate-later settings
  const [rateLaterAutoRemoval, setRateLaterAutoRemoval] = useState(
    pollSettings?.rate_later__auto_remove ?? DEFAULT_RATE_LATER_AUTO_REMOVAL
  );

  // Recommendations (stream)
  const [recoDefaultLanguages, setRecoDefaultLanguages] = useState<
    Array<string>
  >(initialLanguages());

  // Recommendations (page)
  const [recoDefaultUnsafe, setRecoDefaultUnsafe] = useState(
    pollSettings?.recommendations__default_unsafe ?? false
  );
  const [recoDefaultExcludeCompared, setRecoDefaultExcludeCompared] = useState(
    pollSettings?.recommendations__default_exclude_compared_entities ?? false
  );
  const [recoDefaultUploadDate, setRecoDefaultUploadDate] = useState<
    Recommendations_defaultDateEnum | BlankEnum
  >(
    pollSettings?.recommendations__default_date ??
      Recommendations_defaultDateEnum.MONTH
  );

  useEffect(() => {
    if (!generalSettings && !pollSettings) {
      return;
    }

    if (generalSettings?.notifications__lang != undefined) {
      setNotificationsLang(generalSettings.notifications__lang);
    }

    if (generalSettings?.notifications_email__research != undefined) {
      setNotificationsEmailResearch(
        generalSettings.notifications_email__research
      );
    }

    if (generalSettings?.notifications_email__new_features != undefined) {
      setNotificationsEmailNewFeatures(
        generalSettings.notifications_email__new_features
      );
    }

    if (
      pollSettings?.comparison_ui__weekly_collective_goal_display != undefined
    ) {
      setCompUiWeeklyColGoalDisplay(
        pollSettings?.comparison_ui__weekly_collective_goal_display
      );
    }

    if (
      pollSettings?.comparison_ui__weekly_collective_goal_mobile != undefined
    ) {
      setCompUiWeeklyColGoalMobile(
        pollSettings?.comparison_ui__weekly_collective_goal_mobile
      );
    }

    if (pollSettings?.comparison__auto_select_entities != undefined) {
      setAutoSelectEntities(pollSettings?.comparison__auto_select_entities);
    }

    if (pollSettings?.comparison__criteria_order != undefined) {
      setDisplayedCriteria(pollSettings.comparison__criteria_order);
    }

    if (pollSettings?.extension__search_reco != undefined) {
      setExtSearchRecommendation(pollSettings.extension__search_reco);
    }

    if (pollSettings?.rate_later__auto_remove != undefined) {
      setRateLaterAutoRemoval(pollSettings.rate_later__auto_remove);
    }

    if (pollSettings?.recommendations__default_languages != undefined) {
      setRecoDefaultLanguages(pollSettings.recommendations__default_languages);
    }

    if (pollSettings?.recommendations__default_unsafe != undefined) {
      setRecoDefaultUnsafe(pollSettings.recommendations__default_unsafe);
    }

    if (
      pollSettings?.recommendations__default_exclude_compared_entities !=
      undefined
    ) {
      setRecoDefaultExcludeCompared(
        pollSettings.recommendations__default_exclude_compared_entities
      );
    }

    if (pollSettings?.recommendations__default_date != undefined) {
      setRecoDefaultUploadDate(pollSettings.recommendations__default_date);
    }
  }, [generalSettings, pollSettings]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setDisabled(true);

    saveRecommendationsLanguages(recoDefaultLanguages.join(','));

    const response: void | TournesolUserSettings =
      await UsersService.usersMeSettingsPartialUpdate({
        requestBody: {
          general: {
            notifications__lang: notificationsLang,
            notifications_email__research: notificationsEmailResearch,
            notifications_email__new_features: notificationsEmailNewFeatures,
          },
          [YOUTUBE_POLL_NAME]: {
            comparison__criteria_order: displayedCriteria,
            comparison__auto_select_entities: autoSelectEntities,
            comparison_ui__weekly_collective_goal_display:
              compUiWeeklyColGoalDisplay,
            comparison_ui__weekly_collective_goal_mobile:
              compUiWeeklyColGoalMobile,
            extension__search_reco: extSearchRecommendation,
            rate_later__auto_remove: rateLaterAutoRemoval,
            recommendations__default_languages: recoDefaultLanguages,
            recommendations__default_date: recoDefaultUploadDate,
            recommendations__default_unsafe: recoDefaultUnsafe,
            recommendations__default_exclude_compared_entities:
              recoDefaultExcludeCompared,
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
      <Grid
        container
        direction="column"
        alignItems="stretch"
        spacing={mainSectionGridSpacing}
      >
        <SettingsSection
          title={t('preferences.generalPreferences')}
          {...subSectionBreakpoints}
        >
          <GeneralUserSettingsForm
            notificationsLang={notificationsLang}
            setNotificationsLang={setNotificationsLang}
            notificationsEmailResearch={notificationsEmailResearch}
            setNotificationsEmailResearch={setNotificationsEmailResearch}
            notificationsEmailNewFeatures={notificationsEmailNewFeatures}
            setNotificationsEmailNewFeatures={setNotificationsEmailNewFeatures}
          />
        </SettingsSection>
        <SettingsSection
          title={`${t('preferences.preferencesRegarding')} ${t('poll.videos')}`}
          {...subSectionBreakpoints}
        >
          <VideosPollUserSettingsForm
            extSearchRecommendation={extSearchRecommendation}
            setExtSearchRecommendation={setExtSearchRecommendation}
            compAutoSelectEntities={autoSelectEntities}
            setCompAutoSelectEntities={setAutoSelectEntities}
            compUiWeeklyColGoalDisplay={compUiWeeklyColGoalDisplay}
            setCompUiWeeklyColGoalDisplay={setCompUiWeeklyColGoalDisplay}
            compUiWeeklyColGoalMobile={compUiWeeklyColGoalMobile}
            setCompUiWeeklyColGoalMobile={setCompUiWeeklyColGoalMobile}
            displayedCriteria={displayedCriteria}
            setDisplayedCriteria={setDisplayedCriteria}
            rateLaterAutoRemoval={rateLaterAutoRemoval}
            setRateLaterAutoRemoval={setRateLaterAutoRemoval}
            recoDefaultLanguages={recoDefaultLanguages}
            setRecoDefaultLanguages={setRecoDefaultLanguages}
            recoDefaultUnsafe={recoDefaultUnsafe}
            setRecoDefaultUnsafe={setRecoDefaultUnsafe}
            recoDefaultExcludeCompared={recoDefaultExcludeCompared}
            setRecoDefaultExcludeCompared={setRecoDefaultExcludeCompared}
            recoDefaultUploadDate={recoDefaultUploadDate}
            setRecoDefaultUploadDate={setRecoDefaultUploadDate}
            apiErrors={apiErrors}
          />
        </SettingsSection>
      </Grid>
      <Box
        mt={4}
        position="sticky"
        bottom={theme.spacing(2)}
        zIndex={theme.zIndex.fab}
        bgcolor="#fafafa"
      >
        <Grid container>
          <Grid item {...subSectionBreakpoints}>
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
        </Grid>
      </Box>
    </form>
  );
};

export default TournesolUserSettingsForm;
