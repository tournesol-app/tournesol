import React, { useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import {
  ContentBox,
  ContentHeader,
  CriteriaIcon,
  TitledPaper,
} from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import { useLocation } from 'react-router-dom';
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
  const { hash } = useLocation();
  const alreadyScrolled = React.useRef(false);

  useEffect(() => {
    // Do not scroll when it's not required.
    if (hash) {
      // Scroll only one time.
      if (!alreadyScrolled.current) {
        const element = document.getElementById(hash.substring(1));
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
          alreadyScrolled.current = true;
        }
      }
    }
  }, [hash]);

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
