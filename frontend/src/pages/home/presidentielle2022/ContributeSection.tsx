import React from 'react';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Typography, Button, Box } from '@mui/material';

// ContributeSection is a paragraph displayed on the HomePage
// that helps users know how to contribute as users of Tournesol
const ContributeSection = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  return (
    <Box
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h2" gutterBottom>
        {t('home.contributeTitle')}
      </Typography>
      <Typography paragraph>{t('home.contributePollPresidential')}</Typography>
      <Button
        color="primary"
        variant="contained"
        component={Link}
        to={`/${pollName}/comparison?series=true`}
      >
        Compare Candidates Now
      </Button>
    </Box>
  );
};

export default ContributeSection;
