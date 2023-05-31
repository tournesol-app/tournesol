import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const CancellationAndTermination = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="cancellation-and-termination"
      >
        {t(
          'termsOfService.cancellationAndTermination.cancellationAndTermination'
        )}
      </Typography>
      <Box my={2}>
        <Alert severity="info">
          <AlertTitle>
            <strong>{t('termsOfService.shortVersion')}</strong>
          </AlertTitle>
          {t('termsOfService.cancellationAndTermination.shortVersion')}
        </Alert>
      </Box>
      <Typography variant="h5" gutterBottom id="account-cancellation">
        {t(
          'termsOfService.cancellationAndTermination.titles.1accountCancellation'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.cancellationAndTermination.paragraphs.accountCancellation'
        )}
      </Typography>
      <Typography variant="h5" gutterBottom id="upon-cancellation">
        {t(
          'termsOfService.cancellationAndTermination.titles.2uponCancellation'
        )}
      </Typography>
      <Typography paragraph>
        {t('termsOfService.cancellationAndTermination.paragraphs.weWillDelete')}
      </Typography>
      <Typography
        variant="h5"
        gutterBottom
        id="the-tournesol-association-may-terminate"
      >
        {t(
          'termsOfService.cancellationAndTermination.titles.3theTournesolAssociationMayTerminate'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.cancellationAndTermination.paragraphs.theAssociationWillCancel'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.cancellationAndTermination.paragraphs.theTournesolAssociationHasTheRight'
        )}
      </Typography>
      <Typography paragraph>
        {t(
          'termsOfService.cancellationAndTermination.paragraphs.suspendAllAccessInCaseOfThreat'
        )}
      </Typography>
    </Box>
  );
};

export default CancellationAndTermination;