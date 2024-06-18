import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid } from '@mui/material';

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
import ItemsLanguages from './fields/ItemsLanguages';
import RateLaterAutoRemoveField from './fields/RateLaterAutoRemove';
import WeeklyCollectiveGoalDisplayField from './fields/WeeklyCollectiveGoalDisplay';
import RecommendationsDefaultLanguage from './fields/RecommendationsDefaultLanguage';
import FeedForYou from './fieldsets/FeedForYou';
import SettingsHeading from './SettingsHeading';

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
  topVideosLanguages: string[];
  setTopVideosLangauges: (target: string[]) => void;
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
  topVideosLanguages,
  setTopVideosLangauges,
  apiErrors,
}: VideosPollUserSettingsFormProps) => {
  const pollName = YOUTUBE_POLL_NAME;

  const { t } = useTranslation();

  return (
    <Box display="flex" flexDirection="column" rowGap={6}>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <Grid item>
          <SettingsHeading
            id="comparison_page"
            text={t('pollUserSettingsForm.comparisonPage')}
          />
        </Grid>
        <Grid item>
          <WeeklyCollectiveGoalDisplayField
            value={compUiWeeklyColGoalDisplay}
            onChange={setCompUiWeeklyColGoalDisplay}
            pollName={pollName}
          />
        </Grid>
        <Grid
          item
          container
          spacing={1}
          direction="column"
          alignItems="stretch"
        >
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
      </Grid>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <Grid item>
          <SettingsHeading
            id="extension_youtube"
            text={t('pollUserSettingsForm.extensionYoutube')}
          />
        </Grid>
        <Grid item>
          <ExtSearchRecommendation
            value={extSearchRecommendation}
            onChange={setExtSearchRecommendation}
            pollName={pollName}
          />
        </Grid>
      </Grid>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <Grid item>
          <SettingsHeading
            id={`${pollName}-feed-top`}
            text={t('videosUserSettingsForm.feed.topItems.feedTopVideos')}
          />
        </Grid>
        <Grid item>
          <ItemsLanguages
            label={t('videosUserSettingsForm.feed.topItems.topVideosLanguages')}
            helpText={t(
              'videosUserSettingsForm.feed.topItems.keepEmptyToSelectAllLang'
            )}
            value={topVideosLanguages}
            onChange={setTopVideosLangauges}
          />
        </Grid>
      </Grid>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <FeedForYou
          pollName={pollName}
          forYouUnsafe={forYouUnsafe}
          setForYouUnsafe={setForYouUnsafe}
          forYouExcludeCompared={forYouExcludeCompared}
          setForYouExcludeCompared={setForYouExcludeCompared}
          forYouUploadDate={forYouUploadDate}
          setForYouUploadDate={setForYouUploadDate}
        />
      </Grid>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <Grid item>
          <SettingsHeading
            id="rate_later"
            text={t('pollUserSettingsForm.rateLater')}
          />
        </Grid>
        <Grid item>
          <RateLaterAutoRemoveField
            apiErrors={apiErrors}
            value={rateLaterAutoRemoval}
            onChange={setRateLaterAutoRemoval}
            pollName={pollName}
          />
        </Grid>
      </Grid>
      <Grid container spacing={4} direction="column" alignItems="stretch">
        <Grid item>
          <SettingsHeading
            id="recommendations"
            text={t('pollUserSettingsForm.recommendations')}
          />
        </Grid>
        <Grid item>
          <RecommendationsDefaultLanguage
            value={recoDefaultLanguages}
            onChange={setRecoDefaultLanguages}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default VideosPollUserSettingsForm;
