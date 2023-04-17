import { Box, LinearProgress, Typography } from '@mui/material';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useStatsRefresh } from 'src/hooks/useStatsRefresh';

const CollectiveGoalWeeklyProgress = () => {
  const { t } = useTranslation();
  const [totalWeeklyCount, setTotalWeeklyCount] = useState(0);
  const { statsState } = useStatsRefresh();

  console.log('statsState of Progress Bar UI', statsState);

  useEffect(() => {
    setTotalWeeklyCount(statsState.currentWeekComparisonCount);
  }, [statsState.currentWeekComparisonCount]);

  const weeklyPercent = statsState.currentWeekComparisonCount / 10;

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
            {t('comparison.weeklyCollectiveGoal')} - {weeklyPercent}%
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
              value={weeklyPercent}
              color="success"
              sx={{
                width: '100%',
                maxWidth: '400px',
                height: '12px',
                marginRight: '6px',
                borderRadius: '6px',
              }}
            />
            <Typography>{totalWeeklyCount}/1000</Typography>
          </Box>
        </Box>
      </Box>
    </>
  );
};

export default CollectiveGoalWeeklyProgress;
