import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Divider, Grid, Paper, Typography } from '@mui/material';

import { Metrics } from 'src/features/statistics/UsageStatsSection';
import HomeComparison from './HomeComparison';
import SectionTitle from './SectionTitle';

interface ComparisonStats {
  comparisonCount: number;
  lastMonthComparisonCount: number;
}

interface Props {
  comparisonStats?: ComparisonStats;
}

const ComparisonSection = ({ comparisonStats }: Props) => {
  const { t } = useTranslation();

  const color = '#fff';

  return (
    <Box>
      <SectionTitle title={t('comparisonSection.contribute')} />
      <Grid container justifyContent="center" spacing={4}>
        <Grid item lg={3} xl={3}>
          <Box
            display="flex"
            flexDirection="column"
            justifyContent="space-between"
            gap={2}
          >
            <Paper elevation={0}>
              <Box p={2} bgcolor="#1282B2" color={color} borderRadius={1}>
                <Typography paragraph fontSize={17}>
                  {t('comparisonSection.theSimpliestWayToContribute')}
                </Typography>
                <Box pb={2}>
                  <Divider sx={{ backgroundColor: color }} />
                </Box>
                <Box textAlign="center">
                  <Metrics
                    text={t('stats.comparisons')}
                    count={comparisonStats?.comparisonCount || 0}
                    lastMonthCount={
                      comparisonStats?.lastMonthComparisonCount || 0
                    }
                    lastMonthAsText
                  />
                </Box>
              </Box>
            </Paper>
          </Box>
        </Grid>
        <Grid item lg={9} xl={6}>
          <Box display="flex" justifyContent="center">
            <HomeComparison />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComparisonSection;
