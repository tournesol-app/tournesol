import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

const OrientYourCareer = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="orient-your-career"
      >
        {t('actionsPage.orientYourCareer.orientYourCareerToImprove')}
      </Typography>
      <Box my={2}>
        <Alert severity="info" icon={false}>
          {t('actionsPage.orientYourCareer.why')}
        </Alert>
      </Box>
    </Box>
  );
};

export default OrientYourCareer;
