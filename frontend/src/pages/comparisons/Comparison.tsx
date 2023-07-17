import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';
import CollectiveGoalWeeklyProgress from 'src/features/goals/CollectiveGoalWeeklyProgress';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import Tips from 'src/features/tips/Tips';
import {
  BlankEnum,
  ComparisonUi_weeklyCollectiveGoalDisplayEnum,
} from 'src/services/openapi';
import { getUserComparisonsRaw } from 'src/utils/api/comparisons';
import { PollUserSettingsKeys } from 'src/utils/types';

const displayWeeklyCollectiveGoal = (
  userPreference: ComparisonUi_weeklyCollectiveGoalDisplayEnum | BlankEnum,
  isEmbedded: boolean
) => {
  const displayWhenEembedded = [
    ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS,
    ComparisonUi_weeklyCollectiveGoalDisplayEnum.EMBEDDED_ONLY,
  ];

  const displayWhenWebsite = [
    ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS,
    ComparisonUi_weeklyCollectiveGoalDisplayEnum.WEBSITE_ONLY,
  ];

  if (!userPreference) {
    return true;
  }

  if (isEmbedded === true && displayWhenEembedded.includes(userPreference)) {
    return true;
  }

  if (isEmbedded === false && displayWhenWebsite.includes(userPreference)) {
    return true;
  }

  return false;
};

/**
 * Display the standard comparison UI or the poll tutorial.
 *
 * The tutorial is displayed if the `series` URL parameter is present and the
 * poll's tutorial options are configured.
 */
const ComparisonPage = () => {
  const { t } = useTranslation();

  const {
    options,
    baseUrl,
    active: pollActive,
    name: pollName,
  } = useCurrentPoll();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const isEmbedded = Boolean(searchParams.get('embed'));

  const [isLoading, setIsLoading] = useState(true);
  const [comparisonsCount, setComparisonsCount] = useState(0);
  const [userComparisons, setUserComparisons] = useState<string[]>();

  useEffect(() => {
    async function getUserComparisonsAsync(
      pName: string
    ): Promise<[number, string[]]> {
      const paginatedComparisons = await getUserComparisonsRaw(pName, 20);
      let results: string[] = [];

      if (paginatedComparisons.results) {
        results = paginatedComparisons.results.map(
          (c) => c.entity_a.uid + '/' + c.entity_b.uid
        );
      }

      return [paginatedComparisons.count ?? 0, results];
    }

    getUserComparisonsAsync(pollName)
      .then((results) => {
        setComparisonsCount(results[0]);
        setUserComparisons(results[1]);
        setIsLoading(false);
      })
      .catch(() => {
        setIsLoading(false);
      });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Tutorial parameters.
  const tutorialLength = options?.tutorialLength ?? 0;
  const tutorialAlternatives = options?.tutorialAlternatives ?? undefined;
  const tutorialDialogs = options?.tutorialDialogs ?? undefined;
  const tutorialTips = options?.tutorialTips ?? undefined;
  const redirectTo = options?.tutorialRedirectTo ?? '/comparisons';
  const keepUIDsAfterRedirect = options?.tutorialKeepUIDsAfterRedirect ?? true;
  const dialogs = tutorialDialogs ? tutorialDialogs(t) : undefined;

  const tipsTutorialContent = tutorialTips ? tutorialTips(t) : undefined;

  // Only display the DialogBox for the last comparison
  const splitTutorialDialogs = dialogs
    ? { [tutorialLength - 1]: dialogs[tutorialLength - 1] }
    : undefined;

  // User's settings.
  const userSettings = useSelector(selectSettings).settings;
  // By default always display the weekly collective goal.
  const weeklyCollectiveGoalDisplay =
    userSettings?.[pollName as PollUserSettingsKeys]
      ?.comparison_ui__weekly_collective_goal_display ??
    ComparisonUi_weeklyCollectiveGoalDisplayEnum.ALWAYS;

  return (
    <>
      <ContentHeader title={t('comparison.submitAComparison')} />
      <ContentBox>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            flexDirection: 'column',
          }}
        >
          {!pollActive && (
            <Box pb={3} textAlign="center" color="neutral.main">
              <Typography>{t('comparison.inactivePoll')}</Typography>
              <Typography>
                {t(
                  'comparison.inactivePollComparisonCannotBeSubmittedOrEdited'
                )}
              </Typography>
            </Box>
          )}

          {/* We don't use a LoaderWrapper here, as we want to initialize
            ComparisonSeries only when userComparisons has been computed */}
          {!isLoading &&
            (comparisonsCount < tutorialLength ? (
              <>
                <Tips
                  content={tipsTutorialContent}
                  step={comparisonsCount}
                  stopAutoDisplay={tutorialLength}
                />
                <ComparisonSeries
                  step={comparisonsCount}
                  onStepUp={setComparisonsCount}
                  length={tutorialLength}
                  initComparisonsMade={userComparisons ?? []}
                  isTutorial={true}
                  generateInitial={true}
                  dialogs={splitTutorialDialogs}
                  getAlternatives={tutorialAlternatives}
                  redirectTo={`${baseUrl}${redirectTo}`}
                  keepUIDsAfterRedirect={keepUIDsAfterRedirect}
                  resumable={true}
                />
              </>
            ) : (
              <>
                {displayWeeklyCollectiveGoal(
                  weeklyCollectiveGoalDisplay,
                  isEmbedded
                ) && <CollectiveGoalWeeklyProgress />}
                <Comparison />
              </>
            ))}
        </Box>
      </ContentBox>
    </>
  );
};

export default ComparisonPage;
