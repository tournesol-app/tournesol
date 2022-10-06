import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Divider, Grid, Paper, Typography } from '@mui/material';

import { Metrics } from 'src/features/statistics/UsageStatsSection';
import HomeComparison from './HomeComparison';

const ComparisonSection = () => {
  const { t } = useTranslation();

  const color = '#fff';

  return (
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
                  text="Comparisons"
                  count={9999}
                  lastMonthCount={100}
                  verbose
                />
              </Box>
            </Box>
          </Paper>
        </Box>
      </Grid>
    </Grid>
  );
};

export default ComparisonSection;
