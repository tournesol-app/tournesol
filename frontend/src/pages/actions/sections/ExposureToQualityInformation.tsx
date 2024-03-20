import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

const ExposureToQualityInformation = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="exposure-to-quality-information"
      >
        {t(
          'actionsPage.qualityInformation.increaseYourExposureToQualityInformation'
        )}
      </Typography>
    </Box>
  );
};

export default ExposureToQualityInformation;
