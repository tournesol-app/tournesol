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
      <Typography paragraph>
        Tournesol evaluates alternatives using comparisons from contributors.
        Comparisons are based on multiple rating criteria in order to help
        contributors reflect on how to evaluate candidates. By comparing
        candidates you will be included in the collaborative decisions, you will
        provide very valuable data to help research on the ethics of algorithms
        and artificial intelligence and you will receive feedback and insights
        from Tournesol&apos;s algorithms about your explicited preferences.
      </Typography>
      {/* TODO when available this could be replaced by a link to start the tutorial */}
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
