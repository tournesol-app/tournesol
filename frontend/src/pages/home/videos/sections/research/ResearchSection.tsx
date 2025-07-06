import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid } from '@mui/material';

import SectionTitle from '../SectionTitle';
import PublicDataPublicCodeBox from './PublicDataPublicCodeBox';
import ScientificLiteratureBox from './ScientificLiteratureBox';
import VisualizeDataBox from './VisualizeDataBox';
import SectionDescription from '../SectionDescription';

const ResearchSection = () => {
  const { t } = useTranslation();

  return (
    <Box>
      <SectionTitle
        title={t('researchSection.research')}
        headingId="research"
      />
      <SectionDescription
        description={t('researchSection.weSeekToSupportResearch')}
      />
      <Grid
        container
        spacing={4}
        sx={{
          justifyContent: 'center',
        }}
      >
        <Grid item lg={4} xl={4}>
          <PublicDataPublicCodeBox />
        </Grid>
        <Grid item lg={8} xl={5}>
          <VisualizeDataBox />
        </Grid>
        <Grid
          item
          xl={9}
          sx={{
            width: '100%',
          }}
        >
          <ScientificLiteratureBox />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchSection;
