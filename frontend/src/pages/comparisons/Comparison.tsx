import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';
import LinearProgress from '@mui/material/LinearProgress';

import { useStatsRefresh } from 'src/hooks/useStatsRefresh';

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

  const [userWeekly, setUserWeekly] = useState(30);
  const [totalWeekly, setTotalWeekly] = React.useState(70);

  const { statsState } = useStatsRefresh();
  const weeklyPercent = statsState.currentWeekComparisonCount / 10;

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
