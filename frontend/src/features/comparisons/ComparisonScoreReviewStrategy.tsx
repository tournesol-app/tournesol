import React from 'react';

import { useCurrentPoll } from 'src/hooks';
import { ComparisonRequest } from 'src/services/openapi';
import { isMobileDevice } from 'src/utils/extension';

import { SLIDER_SCORE_MAX } from './CriteriaSlider';
import { getCriterionScoreMax } from './ComparisonInputStrategy';
import CriteriaButtonsScoreReview from './inputs/CriteriaButtonsScoreReview';
import { BUTTON_SCORE_MAX } from './inputs/CriterionButtons';

interface ComparisonScoreReviewStrategyProps {
  initialComparison: ComparisonRequest | null;
}

const ComparisonScoreReviewStrategy = ({
  initialComparison,
}: ComparisonScoreReviewStrategyProps) => {
  const { options } = useCurrentPoll();

  const mainScoreMax = getCriterionScoreMax(
    initialComparison?.criteria_scores,
    options?.mainCriterionName
  );

  const buttonsUsed = mainScoreMax == BUTTON_SCORE_MAX;
  const slidersUsed = mainScoreMax == SLIDER_SCORE_MAX;
  const fallBackToButtons = !buttonsUsed && !slidersUsed && isMobileDevice();
  const displayForButtons = buttonsUsed || fallBackToButtons;

  return (
    <>
      {displayForButtons && (
        <CriteriaButtonsScoreReview initialComparison={initialComparison} />
      )}
    </>
  );
};

export default ComparisonScoreReviewStrategy;
