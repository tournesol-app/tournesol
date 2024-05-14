import React from 'react';

import { Box } from '@mui/material';
import { ComparisonRequest } from 'src/services/openapi';
import { CriteriaIcon } from 'src/components';
import { scoreButtons } from './ComparisonCriterionButtons';

interface CriteriaButtonsScoreReviewProps {
  initialComparison: ComparisonRequest | null;
}

const CriteriaButtonsScoreReview = ({
  initialComparison,
}: CriteriaButtonsScoreReviewProps) => {
  if (!initialComparison?.criteria_scores) return <></>;

  return (
    <Box display="flex" justifyContent="space-between" px={1}>
      {scoreButtons.map((scoreBtn) => (
        <Box
          key={scoreBtn.score}
          minWidth="38px"
          display="flex"
          flexDirection="column"
          alignItems="center"
          rowGap={1}
        >
          <Box px={1} color="grey">
            {scoreBtn.icons}
          </Box>

          {initialComparison?.criteria_scores.map((crit) => {
            if (crit.score !== scoreBtn.score) return;

            return (
              <Box key={crit.criteria}>
                <CriteriaIcon criteriaName={crit.criteria} />
              </Box>
            );
          })}
        </Box>
      ))}
    </Box>
  );
};

export default CriteriaButtonsScoreReview;
