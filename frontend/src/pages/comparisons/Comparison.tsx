import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';
import LinearProgress from '@mui/material/LinearProgress';

import { PollStats } from 'src/utils/types';
import { DEFAULT_POLL_STATS, getPollStats } from 'src/utils/api/stats';
import { useNotifications, useLoginState } from 'src/hooks';

/**
 * Display the standard comparison UI or the poll tutorial.
 *
 * The tutorial is displayed if the `series` URL parameter is present and the
 * poll's tutorial options are configured.
 */
const ComparisonPage = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const series: string = searchParams.get('series') || 'false';

  const {
    options,
    baseUrl,
    active: pollActive,
    name: pollName,
  } = useCurrentPoll();

  const tutorialLength = options?.tutorialLength ?? 0;
  const tutorialAlternatives = options?.tutorialAlternatives ?? undefined;
  const tutorialDialogs = options?.tutorialDialogs ?? undefined;
  const redirectTo = options?.tutorialRedirectTo ?? '/comparisons';
  const keepUIDsAfterRedirect = options?.tutorialKeepUIDsAfterRedirect ?? true;
  const dialogs = tutorialDialogs ? tutorialDialogs(t) : undefined;

  // Code for issue solving
  const { isLoggedIn, loginState } = useLoginState();
  const [userWeekly, setUserWeekly] = useState(30); // progress = your current week contribution
  const [totalWeekly, setTotalWeekly] = React.useState(70); // buffer = total current week contribution
  const [stats, setStats] = useState<PollStats>(DEFAULT_POLL_STATS);
  const { showWarningAlert } = useNotifications();

  useEffect(() => {
    async function getPollStatsAsync(pollName: string) {
      try {
        const pollStats = await getPollStats(pollName);
        if (pollStats) {
          setStats(pollStats);
          // setProgress(stats.currentWeekUserComparisonCount) // add logic if logged in user ? their contribution to comparison as well.
          // setBuffer(stats.currentWeekComparisonCount);
        }
      } catch (reason) {
        showWarningAlert(t('home.theStatsCouldNotBeDisplayed'));
      }
    }

    getPollStatsAsync(pollName);
  }, [pollName, showWarningAlert, t]);

  // this const/interface isnt required
  const comparisonStats = {
    comparisonCount: stats.comparisonCount, // no optional chaining since they are already set to 0 as default
    lastMonthComparisonCount: stats.lastThirtyDaysComparisonCount,
    currentWeekComparisonCount: stats.currentWeekComparisonCount,
  };

  console.log('Comparison stats:', comparisonStats);
  console.log('Login State:', isLoggedIn, loginState);

  const weeklyPercent = stats.currentWeekComparisonCount / 10;

  return (
    <>
      <Box>
        Thanks to everyone, Tournesol has reached {weeklyPercent}% of its weekly
        objective of 1000 comparisons.
        <LinearProgress
          variant="buffer"
          value={userWeekly}
          valueBuffer={totalWeekly}
          color="success"
        />
        4,2% comes directly from you! / Help us reach this goal!
      </Box>
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

          {/* shown when we come here from HomeVideos.tsx with series param passed as true */}
          {series === 'true' && tutorialLength > 0 ? (
            <ComparisonSeries
              dialogs={dialogs}
              generateInitial={true}
              getAlternatives={tutorialAlternatives}
              length={tutorialLength}
              redirectTo={`${baseUrl}${redirectTo}`}
              keepUIDsAfterRedirect={keepUIDsAfterRedirect}
              resumable={true}
            />
          ) : (
            <Comparison />
          )}
        </Box>
      </ContentBox>
    </>
  );
};

export default ComparisonPage;
