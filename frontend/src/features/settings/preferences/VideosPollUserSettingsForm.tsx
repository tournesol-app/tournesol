import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, Grid, Typography } from '@mui/material';

import {
  ApiError,
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  Recommendations_defaultDateEnum,
} from 'src/services/openapi';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';

import BooleanField from './fields/generics/BooleanField';
import ComparisonOptionalCriteriaDisplayed from './fields/ComparisonOptionalCriteriaDisplayed';
import ExtSearchRecommendation from './fields/ExtSearchRecommendation';
import RateLaterAutoRemoveField from './fields/RateLaterAutoRemove';
import WeeklyCollectiveGoalDisplayField from './fields/WeeklyCollectiveGoalDisplay';
import RecommendationsDefaultLanguage from './fields/RecommendationsDefaultLanguage';
import RecommendationsDefaultDate from './fields/RecommendationsDefaultDate';

interface VideosPollUserSettingsFormProps {
  extSearchRecommendation: boolean;
  setExtSearchRecommendation: (target: boolean) => void;
  compAutoSelectEntities: boolean;
  setCompAutoSelectEntities: (target: boolean) => void;
  compUiWeeklyColGoalDisplay:
    | ComparisonUi_weeklyCollectiveGoalDisplayEnum
    | BlankEnum;
  setCompUiWeeklyColGoalDisplay: (
    target: ComparisonUi_weeklyCollectiveGoalDisplayEnum | BlankEnum
  ) => void;
  displayedCriteria: string[];
  setDisplayedCriteria: (target: string[]) => void;
  rateLaterAutoRemoval: number;
  setRateLaterAutoRemoval: (number: number) => void;
  recoDefaultLanguages: string[];
  setRecoDefaultLanguages: (target: string[]) => void;
  recoDefaultUnsafe: boolean;
  setRecoDefaultUnsafe: (target: boolean) => void;
  recoDefaultExcludeCompared: boolean;
  setRecoDefaultExcludeCompared: (target: boolean) => void;
  recoDefaultUploadDate: Recommendations_defaultDateEnum | BlankEnum;
  setRecoDefaultUploadDate: (
    target: Recommendations_defaultDateEnum | BlankEnum
  ) => void;
  apiErrors: ApiError | null;
}

/**
 * Display a set of fields representing the preferences of the poll `videos`.
 */
const VideosPollUserSettingsForm = ({
  extSearchRecommendation,
  setExtSearchRecommendation,
  compAutoSelectEntities,
  setCompAutoSelectEntities,
  compUiWeeklyColGoalDisplay,
  setCompUiWeeklyColGoalDisplay,
  displayedCriteria,
  setDisplayedCriteria,
  rateLaterAutoRemoval,
  setRateLaterAutoRemoval,
  recoDefaultLanguages,
  setRecoDefaultLanguages,
  recoDefaultUnsafe,
  setRecoDefaultUnsafe,
  recoDefaultExcludeCompared,
  setRecoDefaultExcludeCompared,
  recoDefaultUploadDate,
  setRecoDefaultUploadDate,
  apiErrors,
}: VideosPollUserSettingsFormProps) => {
  const pollName = YOUTUBE_POLL_NAME;

  const { t } = useTranslation();

  return (
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
      <Grid item>
        <BooleanField
          scope={pollName}
          name="comparison__auto_select_entities"
          label={t('pollUserSettingsForm.letTournesolSuggestElements')}
          value={compAutoSelectEntities}
          onChange={setCompAutoSelectEntities}
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
        <Typography id="extension_youtube" variant="h6">
          {t('pollUserSettingsForm.extensionYoutube')}
        </Typography>
      </Grid>
      <Grid item>
        <ExtSearchRecommendation
          value={extSearchRecommendation}
          onChange={setExtSearchRecommendation}
          pollName={pollName}
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
        <Typography id="recommendations" variant="h6">
          {t('pollUserSettingsForm.recommendations')}
        </Typography>
      </Grid>
      <Grid item>
        <RecommendationsDefaultLanguage
          value={recoDefaultLanguages}
          onChange={setRecoDefaultLanguages}
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
      <Grid item container spacing={1} direction="column" alignItems="stretch">
        <Grid item>
          <BooleanField
            scope={pollName}
            name="recommendations__default_unsafe"
            label={t('videosUserSettingsForm.recommendations.defaultUnsafe')}
            value={recoDefaultUnsafe}
            onChange={setRecoDefaultUnsafe}
          />
        </Grid>
        <Grid item>
          <BooleanField
            scope={pollName}
            name="recommendations__default_exclude_compared_entities"
            label={t(
              'videosUserSettingsForm.recommendations.defaultExcludeCompared'
            )}
            value={recoDefaultExcludeCompared}
            onChange={setRecoDefaultExcludeCompared}
          />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default VideosPollUserSettingsForm;
