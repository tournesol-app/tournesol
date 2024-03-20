import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

const JoinMovements = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="join-movements"
      >
        {t('actionsPage.joinMovements.getInvolvedInDigitalDemocracyMovements')}
      </Typography>
      <Alert severity="info" icon={false}>
        {t('actionsPage.joinMovements.why')}
      </Alert>
    </Box>
  );
};

export default JoinMovements;
