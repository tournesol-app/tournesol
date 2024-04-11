import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, LinearProgress, Typography } from '@mui/material';

import { getPollStats } from 'src/features/statistics/stats';
import { useCurrentPoll, useStats } from 'src/hooks';

import {
  WEEKLY_COMPARISON_GOAL,
  getWeeklyProgressionEmoji,
} from './collective';

const CollectiveGoalWeeklyProgress = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const stats = useStats({ poll: pollName });
  const pollStats = getPollStats(stats, pollName);

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
      mb={{ xs: 2, sm: 4 }}
    >
      <Typography variant="h5" textAlign="center">
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
        &nbsp;
        {`${getWeeklyProgressionEmoji(collectiveComparisonsPercent)}`}
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
