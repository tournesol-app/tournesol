import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Link, Typography } from '@mui/material';
import { Box, Paper } from '@mui/material';

import {
  ContentHeader,
  ContentBoxLegalDocument,
  LegalPaper,
  ContentBox,
} from 'src/components';
import BeEducated from './sections/BeEducated';
import HelpResearchSection from './sections/HelpResearch';

const ActionsPage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader title={'Choisir un titre pour la page action'} />
      <ContentBox maxWidth="md">
        <Typography variant="h3" textAlign="center" mt={4} mb={4}>
          Que pouvez-vous faire pour protéger les sociétés des conséquences des
          intelligences artificielles ?
        </Typography>
        <Box display="flex" flexDirection="column" gap={4}>
          <Paper sx={{ p: 2 }}>
            <BeEducated />
          </Paper>
          <Paper sx={{ p: 2 }}>
            <HelpResearchSection />
          </Paper>
        </Box>
        <Typography variant="h3" textAlign="center" mt={4} mb={4}>
          Que pouvez-vous faire pour vous protéger et protéger vos proches ?
        </Typography>
        <Box display="flex" flexDirection="column" gap={4}>
          <Paper sx={{ p: 2 }}>hello world</Paper>
          <Paper sx={{ p: 2 }}>hello world 2</Paper>
          <Paper sx={{ p: 2 }}>hello world 3</Paper>
          <Paper sx={{ p: 2 }}>hello world 4</Paper>
          <Paper sx={{ p: 2 }}>hello world 5</Paper>
          <Paper sx={{ p: 2 }}>hello world 6</Paper>
        </Box>
      </ContentBox>
    </>
  );
};

export default ActionsPage;
