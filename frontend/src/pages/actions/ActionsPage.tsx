import React from 'react';
import { useTranslation } from 'react-i18next';

import { Typography } from '@mui/material';
import { Box, Paper, useTheme } from '@mui/material';

import { ContentHeader, ContentBox } from 'src/components';
import BeEducated from './sections/BeEducated';
import HelpResearchSection from './sections/HelpResearch';

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
  return <Paper sx={{ p: 2 }}>{children}</Paper>;
};

const ActionsPage = () => {
  const { t } = useTranslation();
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
            <HelpResearchSection key="section_help_research" />,
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
      </ContentBox>
    </>
  );
};

export default ActionsPage;
