import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Typography, Button, Box } from '@mui/material';

// ContributeSection is a paragraph displayed on the HomePage
// that helps users know how to contribute as users of Tournesol
const ContributeSection = () => {
  const { t } = useTranslation();
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
      <Typography paragraph>{t('home.contributeDetail')}</Typography>
      <Button
        color="primary"
        variant="contained"
        component={Link}
        to="/comparison"
      >
        {t('home.compareButton')}
      </Button>
    </Box>
  );
};

export default ContributeSection;
