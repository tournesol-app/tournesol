import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

const AcceptableUse = () => {
  const { t } = useTranslation();
  return (
    <Box>
      <Typography variant="h4" fontStyle="italic" gutterBottom id="moderation">
        {t('termsOfService.acceptableUse')}
      </Typography>
      <Typography variant="h5" gutterBottom id="compliance-with-laws">
        {t('termsOfService.acceptableUse.complianceWithLawsAndRegulation')}
      </Typography>
      <Typography variant="h5" gutterBottom id="user-safety">
        {t('termsOfService.acceptableUse.userSafety')}
      </Typography>
      <Typography variant="h5" gutterBottom id="account-security">
        {t('termsOfService.acceptableUse.inauthenticActivityAndSpam')}
      </Typography>
      <Typography variant="h5" gutterBottom id="service-usage-limits">
        {t('termsOfService.acceptableUse.serviceUsageLimits')}
      </Typography>
    </Box>
  );
};

export default AcceptableUse;
