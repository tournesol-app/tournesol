import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid } from '@mui/material';

import HomeComparison from './HomeComparison';
import SectionTitle from './SectionTitle';
import SectionDescription from './SectionDescription';

const ComparisonSection = () => {
  const { t } = useTranslation();

  return (
    <Box>
      <SectionTitle
        title={t('comparisonSection.contribute')}
        headingId="contribute"
      />
      <SectionDescription
        description={t('comparisonSection.theSimpliestWayToContribute')}
      />
      <Grid
        container
        spacing={4}
        sx={{
          justifyContent: 'center',
        }}
      >
        <Grid
          item
          sx={{
            width: '100%',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <HomeComparison />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComparisonSection;
