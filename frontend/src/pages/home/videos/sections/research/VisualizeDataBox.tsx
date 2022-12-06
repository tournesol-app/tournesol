import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Link, Typography } from '@mui/material';

import TitledPaper from 'src/components/TitledPaper';

const VisualizeDataBox = () => {
  const { t } = useTranslation();

  return (
    <TitledPaper title={t('visualizeDataBox.visualizeTheData')}>
      <Box mb={2} sx={{ '& img': { maxWidth: '100%' } }}>
        <Typography paragraph>
          <Trans i18nKey="visualizeDataBox.youCanQuicklyExploreEtc">
            You can quickly explore our public database with our appplication
            <Link
              color="text.primary"
              href="https://github.com/tournesol-app/tournesol/tree/main/data-visualization"
            >
              Tournesol Data Visualization
            </Link>
            made with Streamlit.
          </Trans>
        </Typography>
        <img
          src="/images/criteria_pearson_correlation_matrix_2022_10_10.png"
          alt={t('visualizeDataBox.personCorrelationCoefficientMatrix')}
        />
      </Box>
      <Box display="flex" justifyContent="center">
        <Typography variant="caption">
          {t('visualizeDataBox.personCorrelationCoefficientMatrix')}
        </Typography>
      </Box>
    </TitledPaper>
  );
};

export default VisualizeDataBox;
