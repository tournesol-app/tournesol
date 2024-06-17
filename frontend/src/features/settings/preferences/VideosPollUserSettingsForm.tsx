import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Alert, Grid, Typography } from '@mui/material';

import {
  ApiError,
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
  FeedForyou_dateEnum,
} from 'src/services/openapi';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';

import BooleanField from './fields/generics/BooleanField';
import ComparisonOptionalCriteriaDisplayed from './fields/ComparisonOptionalCriteriaDisplayed';
import ExtSearchRecommendation from './fields/ExtSearchRecommendation';
import RateLaterAutoRemoveField from './fields/RateLaterAutoRemove';
import WeeklyCollectiveGoalDisplayField from './fields/WeeklyCollectiveGoalDisplay';
import RecommendationsDefaultLanguage from './fields/RecommendationsDefaultLanguage';
import FeedForYouDate from './fields/FeedForYouDate';

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
  compUiWeeklyColGoalMobile: boolean;
  setCompUiWeeklyColGoalMobile: (target: boolean) => void;
  displayedCriteria: string[];
  setDisplayedCriteria: (target: string[]) => void;
  rateLaterAutoRemoval: number;
  setRateLaterAutoRemoval: (number: number) => void;
  recoDefaultLanguages: string[];
  setRecoDefaultLanguages: (target: string[]) => void;
  forYouUnsafe: boolean;
  setForYouUnsafe: (target: boolean) => void;
  forYouExcludeCompared: boolean;
  setForYouExcludeCompared: (target: boolean) => void;
  forYouUploadDate: FeedForyou_dateEnum | BlankEnum;
  setForYouUploadDate: (target: FeedForyou_dateEnum | BlankEnum) => void;
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
  compUiWeeklyColGoalMobile,
  setCompUiWeeklyColGoalMobile,
  displayedCriteria,
  setDisplayedCriteria,
  rateLaterAutoRemoval,
  setRateLaterAutoRemoval,
  recoDefaultLanguages,
  setRecoDefaultLanguages,
  forYouUnsafe,
  setForYouUnsafe,
  forYouExcludeCompared,
  setForYouExcludeCompared,
  forYouUploadDate,
  setForYouUploadDate,
  apiErrors,
}: VideosPollUserSettingsFormProps) => {
  const pollName = YOUTUBE_POLL_NAME;

  const { t } = useTranslation();

  return (
    <Grid container spacing={4} direction="column" alignItems="stretch">
      <Grid item>
        <Typography id="comparison_page" variant="h5">
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
      <Grid item container spacing={1} direction="column" alignItems="stretch">
        <Grid item>
          <BooleanField
            scope={pollName}
            name="comparison_ui__weekly_collective_goal_mobile"
            label={t('pollUserSettingsForm.displayCollectiveGoalOnMobile')}
            value={compUiWeeklyColGoalMobile}
            onChange={setCompUiWeeklyColGoalMobile}
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
        <Typography id="extension_youtube" variant="h5">
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
        <Typography id="rate_later" variant="h5">
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
        <Typography id="recommendations" variant="h5">
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
        <Typography id="feed-foryou" variant="h5">
          {t('pollUserSettingsForm.feedForYou')}
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
        <FeedForYouDate
          value={forYouUploadDate}
          onChange={setForYouUploadDate}
          pollName={pollName}
        />
      </Grid>
      <Grid item container spacing={1} direction="column" alignItems="stretch">
        <Grid item>
          <BooleanField
            scope={pollName}
            name="feed_foryou__unsafe"
            label={t('videosUserSettingsForm.feed.unsafe')}
            value={forYouUnsafe}
            onChange={setForYouUnsafe}
          />
        </Grid>
        <Grid item>
          <BooleanField
            scope={pollName}
            name="feed_foryou__exclude_compared_entities"
            label={t('videosUserSettingsForm.feed.excludeCompared')}
            value={forYouExcludeCompared}
            onChange={setForYouExcludeCompared}
          />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default VideosPollUserSettingsForm;
