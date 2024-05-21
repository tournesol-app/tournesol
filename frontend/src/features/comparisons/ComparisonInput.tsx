import React from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Paper } from '@mui/material';

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

interface ComparisonInputProps {
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

  const main = criteriaScores.find((crit) => crit.criteria === mainCriterion);

  if (main == undefined) {
    return undefined;
  }

  return main.score_max;
};

const ComparisonInput = ({
  uidA,
  uidB,
  initialComparison,
  onSubmit,
  isComparisonPublic,
}: ComparisonInputProps) => {
  const { t } = useTranslation();
  const { options } = useCurrentPoll();

  const mainScoreMax = getCriterionScoreMax(
    initialComparison?.criteria_scores,
    options?.mainCriterionName
  );

  // TODO: decide if isMobileDevice() is the correct method to use.
  const mobileDevice = isMobileDevice();
  const buttonsUsed = mainScoreMax == BUTTON_SCORE_MAX;
  const slidersUsed = mainScoreMax == SLIDER_SCORE_MAX;
  const fallBackToButtons = !buttonsUsed && !slidersUsed && mobileDevice;

  return (
    <>
      {buttonsUsed || fallBackToButtons ? (
        <>
          {!mobileDevice && (
            <Alert icon={false} severity="info">
              {t('comparisonInput.thisComparisonWasMadeOnAMobileDevice')}
            </Alert>
          )}
          <Box display="flex" flexDirection="column" rowGap={1}>
            <CriteriaButtons
              uidA={uidA || ''}
              uidB={uidB || ''}
              onSubmit={onSubmit}
              initialComparison={initialComparison}
            />
            <CriteriaButtonsScoreReview initialComparison={initialComparison} />
          </Box>
        </>
      ) : (
        <>
          {mobileDevice && (
            <Alert icon={false} severity="info">
              {t('comparisonInput.thisComparisonWasMadeOnAComputer')}
            </Alert>
          )}
          <Paper sx={{ py: 2 }}>
            <ComparisonSliders
              submit={onSubmit}
              initialComparison={initialComparison}
              uidA={uidA || ''}
              uidB={uidB || ''}
              isComparisonPublic={isComparisonPublic}
              readOnly={mobileDevice}
            />
          </Paper>
        </>
      )}
    </>
  );
};

export default ComparisonInput;
