import React from 'react';

import { Box, Paper } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import {
  ComparisonCriteriaScoreRequest,
  ComparisonRequest,
} from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/ComparisonSliders';
import { isMobileDevice } from 'src/utils/extension';

import CriteriaButtons from './inputs/CriteriaButtons';
import { BUTTON_SCORE_MAX } from './inputs/CriterionButtons';
import { SLIDER_SCORE_MAX } from './CriteriaSlider';
import CriteriaButtonsScoreReview from './inputs/CriteriaButtonsScoreReview';

interface ComparisonInputStrategyProps {
  uidA: string;
  uidB: string;
  initialComparison: ComparisonRequest | null;
  onSubmit: (c: ComparisonRequest, partialUpdate?: boolean) => Promise<void>;
  isComparisonPublic: boolean;
}

export const getCriterionScoreMax = (
  criteriaScores?: ComparisonCriteriaScoreRequest[],
  mainCriterion?: string
) => {
  if (criteriaScores == undefined || mainCriterion == undefined) {
    return false;
  }

  const found = criteriaScores.find(
    (crit) =>
      crit.criteria === mainCriterion && crit.score_max === BUTTON_SCORE_MAX
  );

  if (found == undefined) {
    return undefined;
  }

  return found.score_max;
};

const ComparisonInputStrategy = ({
  uidA,
  uidB,
  initialComparison,
  onSubmit,
  isComparisonPublic,
}: ComparisonInputStrategyProps) => {
  const { options } = useCurrentPoll();

  const mainScoreMax = getCriterionScoreMax(
    initialComparison?.criteria_scores,
    options?.mainCriterionName
  );

  const buttonsUsed = mainScoreMax == BUTTON_SCORE_MAX;
  const slidersUsed = mainScoreMax == SLIDER_SCORE_MAX;
  // TODO: decide if isMobileDevice() is the correct method to use
  const fallBackToButtons = !buttonsUsed && !slidersUsed && isMobileDevice();

  return (
    <>
      {buttonsUsed || fallBackToButtons ? (
        <Box display="flex" flexDirection="column" rowGap={1}>
          <CriteriaButtons
            uidA={uidA || ''}
            uidB={uidB || ''}
            onSubmit={onSubmit}
            initialComparison={initialComparison}
          />
          <CriteriaButtonsScoreReview initialComparison={initialComparison} />
        </Box>
      ) : (
        <Paper sx={{ py: 2 }}>
          <ComparisonSliders
            submit={onSubmit}
            initialComparison={initialComparison}
            uidA={uidA || ''}
            uidB={uidB || ''}
            isComparisonPublic={isComparisonPublic}
          />
        </Paper>
      )}
    </>
  );
};

export default ComparisonInputStrategy;
