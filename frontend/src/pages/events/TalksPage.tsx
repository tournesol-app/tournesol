import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Button, Link, Typography } from '@mui/material';
import { Email } from '@mui/icons-material';

import GenericEventsPage from 'src/pages/events/GenericEventsPage';
import { EventTypeEnum } from 'src/services/openapi';
import { tournesolTalksMailingListUrl } from 'src/utils/url';

const Header = () => {
  const { t } = useTranslation();

  return (
    <Box sx={{ mb: 4 }}>
      <Typography component="h2" variant="h4" gutterBottom>
        {t('talksPage.whatAreTournesolTalks')}
      </Typography>
      <Typography paragraph>
        {t('talksPage.tournesolTalksIntroduction')}
      </Typography>
      <Box display="flex" justifyContent="flex-end">
        <Button
          size="small"
          variant="text"
          color="secondary"
          startIcon={<Email />}
          component={Link}
          href={tournesolTalksMailingListUrl}
          rel="noopener"
          target="_blank"
        >
          {t('talksPage.beInformedOfUpcomingEvents')}
        </Button>
      </Box>
    </Box>
  );
};

const TalksPage = () => {
  const { t } = useTranslation();
  return (
    <GenericEventsPage
      title={t('talksPage.title')}
      selectedMenuItem="talks"
      eventType={EventTypeEnum.TALK}
      header={<Header />}
    />
  );
};

export default TalksPage;
