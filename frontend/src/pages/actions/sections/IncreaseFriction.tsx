import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

const IncreaseFriction = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="increase-friction"
      >
        {t(
          'actionsPage.increaseFriction.increaseFrictionBetweenYouAndUndesirableInformationUsage'
        )}
      </Typography>
    </Box>
  );
};

export default IncreaseFriction;
