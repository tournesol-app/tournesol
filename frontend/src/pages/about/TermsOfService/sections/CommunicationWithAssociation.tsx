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
        {t(
          'termsOfService.communicationWithAssociation.communicationWithAssociation'
        )}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('termsOfService.shortVersion')}</strong>
          </AlertTitle>
          {t('termsOfService.communicationWithAssociation.shortVersion')}
        </Alert>
      </Box>
      <Typography
        variant="h5"
        gutterBottom
        id="electronic-communication-required"
      >
        {t(
          'termsOfService.communicationWithAssociation.titles.1electronicCommunicationRequired'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.communicationWithAssociation.paragraphs.youConsentToReceiveEmails'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="necessary-emails">
        {t(
          'termsOfService.communicationWithAssociation.titles.2necessaryEmails'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.communicationWithAssociation.paragraphs.necessaryEmails'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="optional-emails">
        {t(
          'termsOfService.communicationWithAssociation.titles.3optionalEmails'
        )}
      </Typography>
    </Box>
  );
};

export default CommunicationWithAssociation;
