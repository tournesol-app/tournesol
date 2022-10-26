import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Divider, Grid, Paper, Typography } from '@mui/material';

import { Metrics } from 'src/features/statistics/UsageStatsSection';
import HomeComparison from './HomeComparison';

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
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        mb={6}
        width="100%"
      >
        <Divider
          component="div"
          role="presentation"
          sx={{ width: { xs: '100%', lg: '75%' } }}
        >
          <Typography
            variant="h1"
            component="h2"
            textAlign="center"
            pl={4}
            pr={4}
          >
            Contribute
          </Typography>
        </Divider>
      </Box>
      <Grid container justifyContent="center" spacing={4}>
        <Grid item lg={6} xl={6}>
          <Box display="flex" justifyContent="center">
            <HomeComparison />
          </Box>
        </Grid>
        <Grid item lg={3} xl={3}>
          <Box
            display="flex"
            flexDirection="column"
            justifyContent="space-between"
            gap={2}
          >
            <Paper square elevation={0}>
              <Box p={2} bgcolor="#1282B2" color={color}>
                <Typography paragraph textAlign="justify" fontSize={17}>
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
      </Grid>
    </Box>
  );
};

export default ComparisonSection;
