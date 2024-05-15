import React from 'react';

import { Paper } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import {
  ComparisonCriteriaScoreRequest,
  ComparisonRequest,
} from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/ComparisonSliders';

import ComparisonCriteriaButtons from './ComparisonCriteriaButtons';
import { BUTTON_SCORE_MAX } from './ComparisonCriterionButtons';

interface ComparisonInputStrategyProps {
  uidA: string;
  uidB: string;
  initialComparison: ComparisonRequest | null;
  onSubmit: (c: ComparisonRequest, partialUpdate?: boolean) => Promise<void>;
  isComparisonPublic: boolean;
}

export const ratedWithInputButtons = (
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

  return found != undefined;
};

const ComparisonInputStrategy = ({
  uidA,
  uidB,
  initialComparison,
  onSubmit,
  isComparisonPublic,
}: ComparisonInputStrategyProps) => {
  const { options } = useCurrentPoll();

  const useButtons = ratedWithInputButtons(
    initialComparison?.criteria_scores,
    options?.mainCriterionName
  );

  return (
    <>
      {useButtons ? (
        <ComparisonCriteriaButtons
          uidA={uidA || ''}
          uidB={uidB || ''}
          onSubmit={onSubmit}
          initialComparison={initialComparison}
        />
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
