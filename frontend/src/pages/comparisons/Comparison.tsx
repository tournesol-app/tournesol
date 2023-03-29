import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, LinearProgress, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';

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

  const { options, baseUrl, active: pollActive } = useCurrentPoll();
  const tutorialLength = options?.tutorialLength ?? 0;
  const tutorialAlternatives = options?.tutorialAlternatives ?? undefined;
  const tutorialDialogs = options?.tutorialDialogs ?? undefined;
  const redirectTo = options?.tutorialRedirectTo ?? '/comparisons';
  const keepUIDsAfterRedirect = options?.tutorialKeepUIDsAfterRedirect ?? true;
  const dialogs = tutorialDialogs ? tutorialDialogs(t) : undefined;

  // Code for issue solving
  // const { isLoggedIn, loginState } = useLoginState();
  const [userWeekly, setUserWeekly] = useState(30); // progress = your current week contribution
  const [totalWeekly, setTotalWeekly] = React.useState(70); // buffer = total current week contribution
  // const [stats, setStats] = useState<PollStats>(DEFAULT_POLL_STATS);

  //new added
  // const stats: PollStats | undefined = useAppSelector(selectStats); // doesn't get automatically updated when we submit a comparison here.
  // console.log('OLD Poll Data is here:', stats);

  // const { statsState } = useStatsRefresh();
  // console.log('STATS STATE:', statsState);

  // console.log('Login State:', isLoggedIn, loginState);

  // const weeklyPercent = statsState.currentWeekComparisonCount / 10;
  const weeklyPercent = 30;

  return (
    <>
      <Box width="100%" justifyContent="space-between">
        <Box
          px={4}
          pt={4}
          pb={2}
          mx={'auto'}
          display="flex"
          flexDirection="column"
          width="100%"
          maxWidth="800px"
          minHeight="100px"
          textAlign="center"
          alignItems="center"
          justifyContent="center"
        >
          <Typography pb={2}>
            <img
              src="/svg/LogoSmall.svg"
              width="18px"
              alt="Should be largely recommended"
              aria-label="Should be largely recommended"
              data-mui-internal-clone-element="true"
            />{' '}
            {t('comparison.thanksForWeeklyObjectiveFirst')} {weeklyPercent}
            {t('comparison.thanksForWeeklyObjectiveSecond')}
          </Typography>
          <LinearProgress
            variant="buffer"
            value={userWeekly} // later set it as : userCurrentWeekComparisonCount
            valueBuffer={totalWeekly} // later set it as : stats?.currentWeekComparisonCount}
            color="success"
            sx={{
              width: '100%',
              maxWidth: '400px',
              height: '12px',
              borderRadius: '6px',
              // borderWidth: '4px'
              '& .MuiLinearProgress-dashed': {
                backgroundColor: 'lightgray', // or gainsboro
                backgroundImage: 'none',
                animation: 'none',
              },
            }}
          />
          <Typography pt={2}>
            4,2% comes directly from you! / {t('comparison.helpReachTheGoal')}
          </Typography>
        </Box>
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
