import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Button, Link } from '@mui/material';

import { useCurrentPoll, useLoginState } from 'src/hooks';

import HomeComparison from './HomeComparison';
import SectionTitle from './SectionTitle';
import SectionDescription from './SectionDescription';

const ComparisonSection = () => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();

  const { isLoggedIn } = useLoginState();

  return (
    <Box>
      <SectionTitle
        title={t('comparisonSection.contribute')}
        headingId="contribute"
      />
      <SectionDescription description={t('home.helpUsAdvanceResearch')} />
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          my: 4,
        }}
      >
        {!isLoggedIn && (
          <Button
            size="large"
            color="inherit"
            variant="outlined"
            component={Link}
            to={`/signup`}
            sx={{
              px: 4,
              mx: 1,
              textAlign: 'center',
              fontSize: '120%',
            }}
          >
            {t('home.generic.createAccount')}
          </Button>
        )}
        <Button
          size="large"
          color="primary"
          variant="contained"
          component={Link}
          to={`${baseUrl}/comparison`}
          sx={{
            px: 4,
            mx: 1,
            fontSize: '120%',
          }}
        >
          {t('home.generic.start')}
        </Button>
      </Box>
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
          lg={9}
          xl={6}
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
