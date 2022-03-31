import React from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Paper, Typography } from '@mui/material';

const Pres2022FeedbackPage = () => {
  const { t } = useTranslation();
  return (
    <>
      <Typography variant="h2" textAlign="center">
        {t('myFeedbackPage.presidentielle2022.subtitle')}
      </Typography>
      <Typography paragraph mt={2} textAlign="justify">
        {t('myFeedbackPage.presidentielle2022.description')}
      </Typography>
      <Grid container spacing={2} textAlign="center">
        <Grid item xs={12} sm={12} md={6}>
          <Paper sx={{ height: '300px' }}>WIP</Paper>
        </Grid>
        <Grid item xs={12} sm={12} md={6}>
          <Paper sx={{ height: '300px' }}>WIP</Paper>
        </Grid>
      </Grid>
    </>
  );
};

export default Pres2022FeedbackPage;
