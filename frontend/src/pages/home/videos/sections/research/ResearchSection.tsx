import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Typography } from '@mui/material';

import SectionTitle from '../SectionTitle';
import PublicDataPublicCodeBox from './PublicDataPublicCodeBox';
import ScientificLiteratureBox from './ScientificLiteratureBox';
import VisualizeDataBox from './VisualizeDataBox';

const ResearchSection = () => {
  const { t } = useTranslation();

  return (
    <Box>
      <SectionTitle
        title={t('researchSection.research')}
        headingId="research"
      />
      <Box display="flex" justifyContent="center" mb={6}>
        <Box sx={{ width: { lg: '44%', xl: '44%' } }}>
          <Typography variant="h3" textAlign="center" letterSpacing="0.8px">
            {t('researchSection.weSeekToSupportResearch')}
          </Typography>
        </Box>
      </Box>
      <Grid container spacing={4} justifyContent="center">
        <Grid item lg={4} xl={4}>
          <PublicDataPublicCodeBox />
        </Grid>
        <Grid item lg={8} xl={5}>
          <VisualizeDataBox />
        </Grid>
        <Grid item xl={9} width="100%">
          <ScientificLiteratureBox />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchSection;
