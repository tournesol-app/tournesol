import React from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import { ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Comparison from 'src/features/comparisons/Comparison';
import ComparisonSeries from 'src/features/comparisonSeries/ComparisonSeries';

const ComparisonPage = () => {
  const { t } = useTranslation();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const series: string = searchParams.get('series') || 'false';

  const { options } = useCurrentPoll();
  const tutorialLength = options?.tutorialLength ?? 0;
  const tutorialAlternatives = options?.tutorialAlternatives ?? undefined;
  const tutorialDialogs = options?.tutorialDialogs ?? undefined;

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
          <ComparisonSeries
            dialogs={tutorialDialogs}
            getAlternatives={tutorialAlternatives}
            length={tutorialLength}
          />
        ) : (
          <Comparison />
        )}
      </Box>
    </>
  );
};

export default ComparisonPage;
