import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const CommunicationWithAssociation = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="communication-with-the-association"
      >
        {t('terms.communicationWithAssociation.communicationWithAssociation')}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('terms.shortVersion')}</strong>
          </AlertTitle>
          {t('terms.communicationWithAssociation.shortVersion')}
        </Alert>
      </Box>
      <Typography
        variant="h5"
        gutterBottom
        id="electronic-communication-required"
      >
        {t(
          'terms.communicationWithAssociation.titles.1electronicCommunicationRequired'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'terms.communicationWithAssociation.paragraphs.youConsentToReceiveEmails'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="necessary-emails">
        {t('terms.communicationWithAssociation.titles.2necessaryEmails')}
      </Typography>
      <Typography paragraph>
        {t('terms.communicationWithAssociation.paragraphs.necessaryEmails')}
      </Typography>
      <Typography paragraph>
        {t(
          'terms.communicationWithAssociation.paragraphs.additionalNecessaryEmails'
        )}
      </Typography>
    </Box>
  );
};

export default CommunicationWithAssociation;
