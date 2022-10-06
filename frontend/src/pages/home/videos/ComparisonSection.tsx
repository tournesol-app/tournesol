import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Paper, Typography } from '@mui/material';

import { Metrics } from 'src/features/statistics/UsageStatsSection';
import HomeComparison from './HomeComparison';

const ComparisonSection = () => {
  const { t } = useTranslation();

  return (
    <Grid container justifyContent="center" spacing={4}>
      <Grid item lg={6} xl={6}>
        <Box display="flex" justifyContent="center">
          <HomeComparison />
        </Box>
      </Grid>
      {/* TODO: move the following item in its own component. */}
      <Grid item lg={3} xl={3}>
        <Box
          display="flex"
          flexDirection="column"
          justifyContent="space-between"
          gap={2}
        >
          <Paper square>
            <Box p={2} pb={0}>
              <Typography paragraph textAlign="justify" fontSize={17}>
                {t('comparisonSection.theSimpliestWayToContribute')}
              </Typography>
            </Box>
          </Paper>
          <Paper square>
            <Box p={2}>
              <Metrics text="Comparisons" count={9999} lastMonthCount={100} />
            </Box>
          </Paper>
        </Box>
      </Grid>
    </Grid>
  );
};

export default ComparisonSection;
