import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import GenericEventsPage from 'src/pages/events/GenericEventsPage';
import { EventTypeEnum } from 'src/services/openapi';

const Header = () => {
  const { t } = useTranslation();

  return (
    <Box sx={{ mb: 4 }}>
      <Typography component="h2" variant="h4" gutterBottom>
        {t('tournesolLivePage.whatAreTheTournesolLive')}
      </Typography>
      <Typography paragraph>
        {t('tournesolLivePage.tournesolLiveIntroduction')}
      </Typography>
    </Box>
  );
};

const TournesolLivePage = () => {
  const { t } = useTranslation();
  return (
    <GenericEventsPage
      title={t('tournesolLivePage.title')}
      selectedMenuItem="live"
      eventType={EventTypeEnum.LIVE}
      header={<Header />}
    />
  );
};

export default TournesolLivePage;
