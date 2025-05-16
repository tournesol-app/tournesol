import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

const ApplicationOfLaws = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
        id="application-of-laws"
        sx={{
          fontStyle: 'italic',
        }}
      >
        {t('actionsPage.applicationOfLaws.demandTheApplicationOfLaws')}
      </Typography>
      <Box
        sx={{
          my: 2,
        }}
      >
        <Alert severity="info" icon={false}>
          {t('actionsPage.applicationOfLaws.why')}
        </Alert>
      </Box>
    </Box>
  );
};

export default ApplicationOfLaws;
