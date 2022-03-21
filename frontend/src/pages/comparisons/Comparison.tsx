import React from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import { ContentHeader } from 'src/components';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';

const ComparisonPage = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);

  const series: string = searchParams.get('series') || 'false';

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
        {series === 'true' ? (
          <ComparisonSeries length={7} messages="it works" />
        ) : (
          <Comparison />
        )}
      </Box>
    </>
  );
};

export default ComparisonPage;
