import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const CommunicationsWithAssociation = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        id="communication-with-the-association"
        sx={{
          fontStyle: 'italic',
        }}
      >
        {t('terms.communicationsWithAssociation.communicationsWithAssociation')}
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
          {t('terms.communicationsWithAssociation.shortVersion')}
        </Alert>
      </Box>
      <Typography
        variant="h5"
        gutterBottom
        id="electronic-communication-required"
      >
        {t(
          'terms.communicationsWithAssociation.titles.1electronicCommunicationRequired'
        )}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.communicationsWithAssociation.p.youConsentToReceiveEmails')}
      </Typography>
      <Typography variant="h5" gutterBottom id="necessary-emails">
        {t('terms.communicationsWithAssociation.titles.2necessaryEmails')}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.communicationsWithAssociation.p.necessaryEmails')}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.communicationsWithAssociation.p.additionalNecessaryEmails')}
      </Typography>
    </Box>
  );
};

export default CommunicationsWithAssociation;
