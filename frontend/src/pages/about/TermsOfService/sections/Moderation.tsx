import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const Moderation = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        id="moderation"
        sx={{
          fontStyle: 'italic',
        }}
      >
        {t('terms.moderation.moderation')}
      </Typography>
      <Box
        sx={{
          my: 2,
        }}
      >
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('terms.shortVersion')}</strong>
          </AlertTitle>
          {t('terms.moderation.shortVersion')}
        </Alert>
      </Box>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.moderation.p.theTournesolAssociationWill')}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.moderation.p.dependingOnTheSeverityWe')}
      </Typography>
      <ul>
        <li>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('terms.moderation.p.accountSuspension')}
          </Typography>
        </li>
        <li>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('terms.moderation.p.accountTermination')}
          </Typography>
        </li>
        <li>
          <Typography
            sx={{
              marginBottom: 2,
            }}
          >
            {t('terms.moderation.p.removalOfAddedContents')}
          </Typography>
        </li>
      </ul>
    </Box>
  );
};

export default Moderation;
