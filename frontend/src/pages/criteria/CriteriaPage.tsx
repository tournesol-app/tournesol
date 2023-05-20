import React from 'react';
import { Box, Typography } from '@mui/material';
import {
  ContentBox,
  ContentHeader,
  CriteriaIcon,
  TitledPaper,
} from 'src/components';
import { useCurrentPoll, useScrollToLocation } from 'src/hooks';
import * as descriptions from './descriptions';
import { useTranslation } from 'react-i18next';

const CriterionDescription = ({ criteriaName }: { criteriaName: string }) => {
  const descComponents: Record<string, React.ElementType> = {
    largely_recommended: descriptions.LargelyRecommended,
    reliability: descriptions.Reliability,
    pedagogy: descriptions.Pedagogy,
    importance: descriptions.Importance,
    layman_friendly: descriptions.LaymanFriendly,
    entertaining_relaxing: descriptions.EntertainingRelaxing,
    engaging: descriptions.Engaging,
    diversity_inclusion: descriptions.DiversityInclusion,
    better_habits: descriptions.BetterHabits,
    backfire_risk: descriptions.BackfireRisk,
  };
  const Desc = descComponents[criteriaName];
  return Desc ? <Desc /> : null;
};

const CriteriaPage = () => {
  const { t } = useTranslation();
  const poll = useCurrentPoll();
  const criteria = poll.criterias;

  useScrollToLocation();

  return (
    <>
      <ContentHeader title={t('comparison.comparisonCriteria')} />
      <ContentBox maxWidth="lg">
        {criteria.map((crit) => {
          const title = (
            <Box display="flex" alignItems="center" gap={2}>
              <CriteriaIcon
                criteriaName={crit.name}
                imgWidth="24px"
                sx={{
                  bgcolor: 'white',
                  p: 1,
                  borderRadius: 1,
                }}
              />
              <Typography variant="h4">{crit.label}</Typography>
            </Box>
          );

          return (
            <TitledPaper
              key={crit.name}
              title={title}
              titleId={crit.name}
              sx={{ mb: 2 }}
            >
              <Typography component="div">
                <CriterionDescription criteriaName={crit.name} />
              </Typography>
            </TitledPaper>
          );
        })}
      </ContentBox>
    </>
  );
};

export default CriteriaPage;
