import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const Moderation = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="moderation">
        {t('termsOfService.moderation.moderation')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('termsOfService.shortVersion')}</strong>
          </AlertTitle>
          {t('termsOfService.moderation.shortVersion')}
        </Alert>
      </Box>
      <Typography paragraph>
        {t('termsOfService.moderation.paragraphs.theTournesolAssociationWill')}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.moderation.paragraphs.dependingOnTheSeverityWe')}
      </Typography>
      <ul>
        <li>
          <Typography paragraph>
            {t('termsOfService.moderation.paragraphs.accountSuspension')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('termsOfService.moderation.paragraphs.accountTermination')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('termsOfService.moderation.paragraphs.removalOfAddedContents')}
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default Moderation;
