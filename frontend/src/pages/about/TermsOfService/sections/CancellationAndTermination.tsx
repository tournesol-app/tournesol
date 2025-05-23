import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, AlertTitle, Box, Typography } from '@mui/material';

const CancellationAndTermination = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        id="cancellation-and-termination"
        sx={{
          fontStyle: 'italic',
        }}
      >
        {t('terms.cancellationAndTermination.cancellationAndTermination')}
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
          {t('terms.cancellationAndTermination.shortVersion')}
        </Alert>
      </Box>
      <Typography variant="h5" gutterBottom id="account-cancellation">
        {t('terms.cancellationAndTermination.titles.1accountCancellation')}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.cancellationAndTermination.p.accountCancellation')}
      </Typography>
      <Typography variant="h5" gutterBottom id="upon-cancellation">
        {t('terms.cancellationAndTermination.titles.2uponCancellation')}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.cancellationAndTermination.p.weWillDelete')}
      </Typography>
      <Typography
        variant="h5"
        gutterBottom
        id="the-tournesol-association-may-terminate"
      >
        {t(
          'terms.cancellationAndTermination.titles.3theTournesolAssociationMayTerminate'
        )}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.cancellationAndTermination.p.theAssociationWillCancel')}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t(
          'terms.cancellationAndTermination.p.theTournesolAssociationHasTheRight'
        )}
      </Typography>
      <Typography
        sx={{
          marginBottom: 2,
        }}
      >
        {t('terms.cancellationAndTermination.p.suspendAllAccessInCaseOfThreat')}
      </Typography>
    </Box>
  );
};

export default CancellationAndTermination;
