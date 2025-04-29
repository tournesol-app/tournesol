import React from 'react';

import { Trans, useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';

import { TitledPaper } from 'src/components';

interface KeyIndicatorProps {
  children: React.ReactNode;
  variant?: 'main' | 'secondary';
}

const KeyIndicator = ({ children, variant }: KeyIndicatorProps) => {
  let color = 'secondary.main';
  let fontSize = '4rem';

  switch (variant) {
    case 'secondary':
      color = 'text.secondary';
      fontSize = '3em';
  }

  return (
    <Typography
      sx={{
        '& strong': {
          color: color,
          fontSize: fontSize,
        },
      }}
    >
      {children}
    </Typography>
  );
};

/**
 * TODO: make this component generic
 * TODO: move this component in the components folder
 */
const UserActivityStats = () => {
  const { t } = useTranslation();

  const value1 = 24;
  const value2 = 1197;

  return (
    <TitledPaper title={t('userActivityStats.comparisons.title')}>
      <Grid container minHeight="300px">
        <Grid
          xs={12}
          sm={12}
          md={4}
          display="flex"
          flexDirection="column"
          justifyContent="center"
        >
          <Box display="flex" alignItems="flex-end" gap={1}>
            <KeyIndicator>
              <Trans
                t={t}
                i18nKey="userActivityStats.comparisons.theLast30Days"
              >
                <strong>{{ value1 }}</strong> the last 30 days
              </Trans>
            </KeyIndicator>
          </Box>
          <Box display="flex" alignItems="flex-end" gap={1}>
            <KeyIndicator variant="secondary">
              <Trans t={t} i18nKey="userActivityStats.comparisons.total">
                <strong>{{ value2 }}</strong> in total
              </Trans>
            </KeyIndicator>
          </Box>
        </Grid>
        <Grid xs={12} sm={12} md={8}>
        </Grid>
      </Grid>
      {/* TODO: create a dedicated component */}
      <Box mt={2} display="flex" flexDirection="column" gap={2}>
        <Alert severity="success">
          🏅 You are one of the top 10 contributors this month.
        </Alert>
        <Alert severity="success">
          🏆 You are one of the top 10% of all-time contributors.
          Congratulations!
        </Alert>
      </Box>
    </TitledPaper>
  );
};

export default UserActivityStats;
