import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

const Donate = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="donate">
        {t(
          'actionsPage.donate.donateToOrganisationsFightingForQualityOfInformation'
        )}
      </Typography>
      <Alert severity="info" icon={false}>
        {t('actionsPage.donate.why')}
      </Alert>
    </Box>
  );
};

export default Donate;
