import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

const ApplicationOfLaws = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="application-of-laws"
      >
        {t('actionsPage.applicationOfLaws.demandTheApplicationOfLaws')}
      </Typography>
      <Alert severity="info" icon={false}>
        {t('actionsPage.applicationOfLaws.why')}
      </Alert>
    </Box>
  );
};

export default ApplicationOfLaws;
