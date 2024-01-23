import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Divider, Grid, Paper, Typography } from '@mui/material';

import { Metrics } from 'src/features/statistics/UsageStatsSection';
import { getPollStats } from 'src/features/statistics/stats';
import { useCurrentPoll, useStats } from 'src/hooks';

import HomeComparison from './HomeComparison';
import SectionTitle from './SectionTitle';

const ComparisonSection = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const stats = useStats({ poll: pollName });
  const pollStats = getPollStats(stats, pollName);

  const color = '#fff';

  return (
    <Box>
      <SectionTitle
        title={t('comparisonSection.contribute')}
        headingId="contribute"
      />
      <Grid container justifyContent="center" spacing={4}>
        <Grid item lg={3} xl={3}>
          <Paper elevation={0}>
            <Box
              p={2}
              bgcolor="background.emphatic"
              color={color}
              borderRadius={1}
            >
              <Typography paragraph fontSize={17}>
                {t('comparisonSection.theSimpliestWayToContribute')}
              </Typography>
              <Box pb={2}>
                <Divider sx={{ backgroundColor: color }} />
              </Box>
              <Box textAlign="center">
                <Metrics
                  text={t('stats.comparisons')}
                  count={pollStats?.comparisons.total ?? 0}
                  lastMonthCount={
                    pollStats?.comparisons.added_last_30_days ?? 0
                  }
                  lastMonthAsText
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
        <Grid item lg={9} xl={6} width="100%">
          <Box display="flex" justifyContent="center">
            <HomeComparison />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComparisonSection;
