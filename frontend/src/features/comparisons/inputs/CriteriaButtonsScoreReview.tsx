import React from 'react';

import { Box, Zoom } from '@mui/material';

import { CriteriaIcon } from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import { ComparisonRequest } from 'src/services/openapi';

import { scoreButtons } from './CriterionButtons';

interface CriteriaButtonsScoreReviewProps {
  initialComparison: ComparisonRequest | null;
}

const CriteriaButtonsScoreReview = ({
  initialComparison,
}: CriteriaButtonsScoreReviewProps) => {
  const { criterias } = useCurrentPoll();

  const orderedCriteriaScores = criterias
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
    <Box display="flex" justifyContent="space-between" px={1}>
      {scoreButtons.map((scoreBtn) => (
        <Box
          key={scoreBtn.score}
          display="flex"
          flexDirection="column"
          alignItems="center"
          rowGap={1}
        >
          <Box px={1} color="grey">
            {scoreBtn.icons}
          </Box>

          {orderedCriteriaScores.map((crit) => {
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
