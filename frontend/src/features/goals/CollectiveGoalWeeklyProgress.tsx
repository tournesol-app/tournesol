import React from 'react';
import { useSelector } from 'react-redux';
import { Trans, useTranslation } from 'react-i18next';

import { Box, LinearProgress, Typography } from '@mui/material';

import { selectStats } from 'src/features/comparisons/statsSlice';
import { useCurrentPoll } from 'src/hooks';

import {
  WEEKLY_COMPARISON_GOAL,
  getWeeklyProgressionEmoji,
} from './collective';

const CollectiveGoalWeeklyProgress = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const publicStats = useSelector(selectStats);

  const pollStats = publicStats.polls.find((poll) => {
    if (poll.name === pollName) {
      return poll;
    }
  });

  const collectiveComparisonsNbr =
    pollStats?.comparisons.added_current_week ?? 0;

  const collectiveComparisonsPercent =
    (collectiveComparisonsNbr / WEEKLY_COMPARISON_GOAL) * 100;

  return (
    <Box
      width="100%"
      display="flex"
      flexDirection="column"
      alignItems="center"
      gap={1}
      mb={4}
    >
      <Typography variant="h6">
        <Trans
          t={t}
          i18nKey="collectiveGoalWeeklyProgress.weeklyCollectiveGoal"
        >
          Weekly collective goal -{' '}
          {{
            collectiveComparisonsPercent:
              collectiveComparisonsPercent.toFixed(1),
          }}
          %
        </Trans>
        {` ${getWeeklyProgressionEmoji(collectiveComparisonsPercent)}`}
      </Typography>
      <Box
        width="100%"
        maxWidth="sm"
        display="flex"
        alignItems="center"
        justifyContent="center"
        gap={1}
      >
        <LinearProgress
          value={Math.min(collectiveComparisonsPercent, 100)}
          color="success"
          variant="determinate"
          sx={{
            width: '100%',
            height: '12px',
            marginRight: '6px',
            borderRadius: '6px',
          }}
        />
        <Typography variant="body1">
          {collectiveComparisonsNbr}/{WEEKLY_COMPARISON_GOAL}
        </Typography>
      </Box>
    </Box>
  );
};

export default CollectiveGoalWeeklyProgress;
