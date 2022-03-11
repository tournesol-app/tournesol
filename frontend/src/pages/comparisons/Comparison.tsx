import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import { ContentHeader } from 'src/components';
import Comparison from 'src/features/comparisons/Comparison';

const ComparisonPage = () => {
  const { t } = useTranslation();

  return (
    <>
      <ContentHeader title={t('comparison.submitAComparison')} />
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          flexDirection: 'column',
          py: 2,
        }}
      >
        <Comparison />
      </Box>
    </>
  );
};

export default ComparisonPage;
