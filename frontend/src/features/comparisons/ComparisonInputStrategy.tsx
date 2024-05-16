import React from 'react';

import { Paper } from '@mui/material';

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
        <CriteriaButtons
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
