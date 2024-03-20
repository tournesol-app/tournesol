import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

const BeWellSurrounred = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ '& li': { mt: 1 } }}>
      <Typography
        variant="h4"
        fontStyle="italic"
        gutterBottom
        id="be-well-surrounred"
      >
        {t('actionsPage.beWellSurrounred.beWellSurrounred')}
      </Typography>
    </Box>
  );
};

export default BeWellSurrounred;
