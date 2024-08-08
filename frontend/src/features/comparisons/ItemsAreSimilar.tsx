import React from 'react';
import { useTranslation } from 'react-i18next';

import { Typography } from '@mui/material';

const ItemsAreSimilar = () => {
  const { t } = useTranslation();

  return (
    <Typography textAlign="center">
      {t('comparison.itemsAreSimilar')}
      {' 🌻'}
    </Typography>
  );
};

export default ItemsAreSimilar;
