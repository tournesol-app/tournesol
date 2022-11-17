import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Box, Link, Paper, Typography } from '@mui/material';

const VisualizeDataBox = () => {
  const { t } = useTranslation();

  return (
    <Paper>
      <Box
        p={2}
        color="#fff"
        bgcolor="#1282B2"
        sx={{
          borderTopLeftRadius: 'inherit',
          borderTopRightRadius: 'inherit',
        }}
      >
        <Typography variant="h4">
          {t('visualizeDataBox.visualizeTheData')}
        </Typography>
      </Box>
      <Box px={2} sx={{ '& img': { maxWidth: '100%' } }}>
        <Box p={2}>
          <Typography paragraph mb={0}>
            <Trans i18nKey="visualizeDataBox.youCanQuicklyExploreEtc">
              You can quickly explore our public database with our appplication
              <Link
                color="text.primary"
                href="https://github.com/tournesol-app/tournesol/tree/main/analytics"
              >
                Tournesol Data Visualization
              </Link>
              made with Streamlit.
            </Trans>
          </Typography>
        </Box>
        <img
          src="/images/criteria_pearson_correlation_matrix_2022_10_10.png"
          alt={t('visualizeDataBox.personCorrelationCoefficientMatrix')}
        />
      </Box>
    </Paper>
  );
};

export default VisualizeDataBox;
