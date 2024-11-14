import React, { useContext, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';

import {
  Alert,
  Box,
  LinearProgress,
  Paper,
  useMediaQuery,
} from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import { useOrderedCriteria } from 'src/hooks/useOrderedCriteria';
import { ComparisonRequest } from 'src/services/openapi';
import ComparisonSliders from 'src/features/comparisons/ComparisonSliders';
import { TutorialContext } from 'src/features/comparisonSeries/TutorialContext';
import { getCriterionScoreMax } from 'src/utils/criteria';
import { ComparisonsContext } from 'src/pages/comparisons/Comparison';

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

interface PositionBarProps {
  position: number;
  initialComparison: ComparisonRequest | null;
}

const PositionBar = ({ position, initialComparison }: PositionBarProps) => {
  const tutorial = useContext(TutorialContext);
  const { options, criterias } = useCurrentPoll();
  const displayedCriteria = useOrderedCriteria();

  const criterion = displayedCriteria[position];
  const criterionScore = initialComparison?.criteria_scores.find(
    (crit) => crit.criteria === criterion.name
  );

  const progressHidden =
    tutorial.isActive ||
    (criterion.name === options?.mainCriterionName &&
      criterionScore == undefined);

  if (progressHidden) {
    return <></>;
  }

  return (
    <LinearProgress
      variant="determinate"
      value={((position + 1) / criterias.length) * 100}
    />
  );
};

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
  const comparisonsContext = useContext(ComparisonsContext);
  const location = useLocation();

  const pointerFine = useMediaQuery('(pointer:fine)', { noSsr: true });

  // Position of the displayed criterion in the list of criteria.
  const [position, setPosition] = useState(0);

  const mainScoreMax = getCriterionScoreMax(
    initialComparison?.criteria_scores,
    options?.mainCriterionName
  );

  const debugInput = new URLSearchParams(location.search).get('debugInput');
  const buttonsDebugEnabled =
    import.meta.env.REACT_APP_ENABLE_COMP_DEBUG_INPUT &&
    debugInput === 'buttons';

  const buttonsUsed = mainScoreMax == BUTTON_SCORE_MAX;
  const slidersUsed = mainScoreMax == SLIDER_SCORE_MAX;
  const fallBackToButtons =
    !buttonsUsed && !slidersUsed && (!pointerFine || buttonsDebugEnabled);

  const changePosition = (newPos: number) => {
    setPosition(newPos);
    if (position === criterias.length - 1 && newPos === 0) {
      comparisonsContext.setHasLoopedThroughCriteria?.(true);
    } else {
      comparisonsContext.setHasLoopedThroughCriteria?.(false);
    }
  };

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
              onPositionChanged={changePosition}
              initialComparison={initialComparison}
            />
            <PositionBar
              position={position}
              initialComparison={initialComparison}
            />
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
