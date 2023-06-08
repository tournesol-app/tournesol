import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const Moderation = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="moderation">
        {t('terms.moderation.moderation')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('terms.shortVersion')}</strong>
          </AlertTitle>
          {t('terms.moderation.shortVersion')}
        </Alert>
      </Box>
      <Typography paragraph>
        {t('terms.moderation.paragraphs.theTournesolAssociationWill')}
      </Typography>
      <Typography paragraph>
        {t('terms.moderation.paragraphs.dependingOnTheSeverityWe')}
      </Typography>
      <ul>
        <li>
          <Typography paragraph>
            {t('terms.moderation.paragraphs.accountSuspension')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('terms.moderation.paragraphs.accountTermination')}
          </Typography>
        </li>
        <li>
          <Typography paragraph>
            {t('terms.moderation.paragraphs.removalOfAddedContents')}
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default Moderation;
