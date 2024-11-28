import React from 'react';

import { Box, Zoom, useTheme } from '@mui/material';

import { CriteriaIcon } from 'src/components';
import { ComparisonRequest } from 'src/services/openapi';

import { scoreButtons } from './CriterionButtons';
import { useOrderedCriteria } from 'src/hooks/useOrderedCriteria';

interface CriteriaButtonsScoreReviewProps {
  initialComparison: ComparisonRequest | null;
}

const CriteriaButtonsScoreReview = ({
  initialComparison,
}: CriteriaButtonsScoreReviewProps) => {
  const theme = useTheme();
  const orderedCriteria = useOrderedCriteria();

  const displayedCriteriaScores = orderedCriteria
    .map((criterion) => {
      const ratedCrit = initialComparison?.criteria_scores.find(
        (crit) => crit.criteria === criterion.name
      );
      if (ratedCrit) {
        return ratedCrit;
      }
    })
    .filter((crit) => crit != undefined);

  if (!initialComparison?.criteria_scores) return <></>;

  return (
    <Box
      px={1}
      display="flex"
      sx={{ justifyContent: { xs: 'space-between', md: 'space-around' } }}
      // Allow the CriterionButtons to slide behind this component.
      zIndex={theme.zIndex.comparisonElevation1}
    >
      {scoreButtons.map((scoreBtn) => (
        <Box
          key={scoreBtn.score}
          display="flex"
          flexDirection="column"
          alignItems="center"
          rowGap={1}
        >
          <Box px={1} color="grey.500" sx={{ height: '1.8rem' }}>
            {scoreBtn.icons}
          </Box>

          {displayedCriteriaScores.map((crit) => {
            if (crit == undefined) return;
            if (crit.score !== scoreBtn.score) return;

            return (
              <Zoom in={true} key={crit.criteria}>
                <Box>
                  <CriteriaIcon criteriaName={crit.criteria} />
                </Box>
              </Zoom>
            );
          })}
        </Box>
      ))}
    </Box>
  );
};

export default CriteriaButtonsScoreReview;
