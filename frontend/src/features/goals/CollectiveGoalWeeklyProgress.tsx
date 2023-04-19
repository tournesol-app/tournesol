import React from 'react';
import { useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';

import { Box, LinearProgress, Typography } from '@mui/material';

import { selectStats } from 'src/features/comparisons/statsSlice';
import { useCurrentPoll } from 'src/hooks';

const WEEKLY_COMPARISON_GOAL = 1000;

const CollectiveGoalWeeklyProgress = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const publicStats = useSelector(selectStats);

  const pollStats = publicStats.polls.find((poll) => {
    if (poll.name === pollName) {
      return poll;
    }
  });

  const collectiveComparisonNbr =
    pollStats?.comparisons.added_current_week ?? 0;
  const collectiveComparisonPercent =
    (collectiveComparisonNbr / WEEKLY_COMPARISON_GOAL) * 100;

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
              alt="tournesol-logo"
              aria-label="tournesol-logo"
              data-mui-internal-clone-element="true"
            />{' '}
            {t('comparison.weeklyCollectiveGoal')} -{' '}
            {collectiveComparisonPercent}%
          </Typography>
          <Box
            width="100%"
            display="flex"
            alignItems="center"
            justifyContent="space-around"
            maxWidth="460px"
          >
            <LinearProgress
              variant="determinate"
              value={collectiveComparisonPercent}
              color="success"
              sx={{
                width: '100%',
                maxWidth: '400px',
                height: '12px',
                marginRight: '6px',
                borderRadius: '6px',
              }}
            />
            <Typography>
              {collectiveComparisonNbr}/{WEEKLY_COMPARISON_GOAL}
            </Typography>
          </Box>
        </Box>
      </Box>
    </>
  );
};

export default CollectiveGoalWeeklyProgress;
