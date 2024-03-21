import React from 'react';
import { useTranslation } from 'react-i18next';

import { Typography } from '@mui/material';
import { Box, Paper, useTheme } from '@mui/material';

import { ContentHeader, ContentBox } from 'src/components';
import { useScrollToLocation } from 'src/hooks';

import ApplicationOfLaws from './sections/ApplicationOfLaws';
import BeEducated from './sections/BeEducated';
import BeWellSurrounred from './sections/BeWellSurrounred';
import Donate from './sections/Donate';
import ExposureToQualityInformation from './sections/ExposureToQualityInformation';
import HelpResearch from './sections/HelpResearch';
import IncreaseFriction from './sections/IncreaseFriction';
import JoinMovements from './sections/JoinMovements';
import OrientYourCareer from './sections/OrientYourCareer';
import Volition from './sections/Volition';

export const ActionQuestion = ({
  question,
  mt = 2,
}: {
  question: string;
  mt?: number;
}) => {
  const theme = useTheme();
  return (
    <Box
      bgcolor={theme.palette.background.emphatic}
      color="white"
      mt={mt}
      mb={4}
      p={2}
    >
      <Typography variant="h3" textAlign="center">
        {question}
      </Typography>
    </Box>
  );
};

export const ActionPaper = ({ children }: { children: React.ReactNode }) => {
  return (
    <Paper
      sx={{
        p: 2,
        '& li': { mt: 1 },
      }}
    >
      {children}
    </Paper>
  );
};

const ActionsPage = () => {
  const { t } = useTranslation();
  useScrollToLocation();

  return (
    <>
      <ContentHeader title={t('actionsPage.title')} />
      <ContentBox maxWidth="md">
        <ActionQuestion
          question={t('actionsPage.whatCanYouDoToProtectSocietiesFromAIs')}
        />
        <Box display="flex" flexDirection="column" gap={4}>
          {[
            <BeEducated key="section_be_educated" />,
            <HelpResearch key="section_help_research" />,
            <Volition key="section_volition" />,
            <ApplicationOfLaws key="section_application_of_law" />,
            <JoinMovements key="section_join_movements" />,
            <OrientYourCareer key="section_orient_your_career" />,
            <Donate key="section_donate" />,
          ].map((section) => (
            <ActionPaper key={`paper_${section.key}`}>{section}</ActionPaper>
          ))}
        </Box>
        <ActionQuestion
          mt={4}
          question={t(
            'actionsPage.whatCanYouDoToProtectYourselfAndYourRelatives'
          )}
        />
        <Box display="flex" flexDirection="column" gap={4}>
          {[
            <IncreaseFriction key="section_increase_friction" />,
            <ExposureToQualityInformation key="section_exposure_to_quality" />,
            <BeWellSurrounred key="section_be_well_surrounred" />,
          ].map((section) => (
            <ActionPaper key={`paper_${section.key}`}>{section}</ActionPaper>
          ))}
        </Box>
      </ContentBox>
    </>
  );
};

export default ActionsPage;
