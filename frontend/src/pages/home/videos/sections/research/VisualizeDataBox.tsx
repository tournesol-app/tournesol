import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Typography } from '@mui/material';

import { ExternalLink, TitledPaper } from 'src/components';

const VisualizeDataBox = () => {
  const { t } = useTranslation();

  return (
    <TitledPaper title={t('visualizeDataBox.visualizeTheData')}>
      <Box mb={2} sx={{ '& img': { maxWidth: '100%' } }}>
        <Typography paragraph>
          <Trans i18nKey="visualizeDataBox.youCanQuicklyExploreEtc">
            You can quickly explore our public database with our appplication
            <ExternalLink href="https://github.com/tournesol-app/tournesol/tree/main/data-visualization">
              Tournesol Data Visualization
            </ExternalLink>
            made with Streamlit.
          </Trans>
        </Typography>
        <img
          src="/images/criteria_pearson_correlation_matrix_2023_06_13.png"
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
