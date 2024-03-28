import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

const ApplicationOfLaws = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="application-of-laws"
      >
        {t('actionsPage.applicationOfLaws.demandTheApplicationOfLaws')}
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.applicationOfLaws.why')}
        </Alert>
      </Box>
    </Box>
  );
};

export default ApplicationOfLaws;
