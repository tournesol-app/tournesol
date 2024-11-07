import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  Box,
  LinearProgress,
  Paper,
  Typography,
  useMediaQuery,
} from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import { ComparisonRequest } from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/ComparisonSliders';

import CriteriaButtons from './inputs/CriteriaButtons';
import { BUTTON_SCORE_MAX } from './inputs/CriterionButtons';
import { SLIDER_SCORE_MAX } from './CriteriaSlider';
import CriteriaButtonsScoreReview from './inputs/CriteriaButtonsScoreReview';
import { getCriterionScoreMax } from 'src/utils/criteria';

interface ComparisonInputProps {
  uidA: string;
  uidB: string;
  initialComparison: ComparisonRequest | null;
  onSubmit: (c: ComparisonRequest, partialUpdate?: boolean) => Promise<void>;
  isComparisonPublic: boolean;
}

/**
 * A component displaying different comparison inputs depending to the user's
 * device.
 */
const ComparisonInput = ({
  uidA,
  uidB,
  initialComparison,
  onSubmit,
  isComparisonPublic,
}: ComparisonInputProps) => {
  const { t } = useTranslation();
  const { options, criterias } = useCurrentPoll();
  const pointerFine = useMediaQuery('(pointer:fine)', { noSsr: true });

  const mainScoreMax = getCriterionScoreMax(
    initialComparison?.criteria_scores,
    options?.mainCriterionName
  );

  const buttonsUsed = mainScoreMax == BUTTON_SCORE_MAX;
  const slidersUsed = mainScoreMax == SLIDER_SCORE_MAX;
  const fallBackToButtons = !buttonsUsed && !slidersUsed && !pointerFine;

  const progress = initialComparison?.criteria_scores.length
    ? (initialComparison?.criteria_scores.length / criterias.length) * 100
    : 0;

  return (
    <>
      {buttonsUsed || fallBackToButtons ? (
        <>
          {pointerFine && (
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
            <Box
              display="flex"
              flexDirection="row"
              alignItems="center"
              columnGap={2}
            >
              <Box width="100%">
                <LinearProgress
                  color="success"
                  variant="determinate"
                  value={progress}
                />
              </Box>
              <Typography color="text.secondary">
                <strong>{progress}%</strong>
              </Typography>
            </Box>
            <CriteriaButtonsScoreReview initialComparison={initialComparison} />
          </Box>
        </>
      ) : (
        <>
          {!pointerFine && (
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
              readOnly={!pointerFine}
            />
          </Paper>
        </>
      )}
    </>
  );
};

export default ComparisonInput;
