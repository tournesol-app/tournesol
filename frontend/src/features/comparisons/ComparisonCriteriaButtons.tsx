import React, { useState } from 'react';
import { useDrag } from '@use-gesture/react';
import { Vector2 } from '@use-gesture/core/types';

import { Box, IconButton, Slide } from '@mui/material';
import { ArrowDropDown, ArrowDropUp } from '@mui/icons-material';

import ComparisonCriterionButtons, {
  BUTTON_SCORE_MAX,
} from 'src/features/comparisons/ComparisonCriterionButtons';
import { useCurrentPoll } from 'src/hooks';
import { ComparisonRequest } from 'src/services/openapi';
import { useTranslation } from 'react-i18next';

const SWIPE_TIMEOUT = 225;
const SWIPE_VELOCITY: number | Vector2 = [0.25, 0.25];

interface ComparisonCriteriaButtonsProps {
  uidA: string;
  uidB: string;
  initialComparison: ComparisonRequest | null;
  onSubmit: (c: ComparisonRequest, partialUpdate?: boolean) => Promise<void>;
}

const ComparisonCriteriaButtons = ({
  uidA,
  uidB,
  initialComparison,
  onSubmit,
}: ComparisonCriteriaButtonsProps) => {
  const { t } = useTranslation();
  const { criterias, name: pollName } = useCurrentPoll();

  const [slideIn, setSlideIn] = useState(true);
  const [slideDirection, setSlideDirection] = useState<'up' | 'down'>('down');
  const [disableButtons, setDisableButtons] = useState(false);

  const [critPosition, setCritPosition] = useState(0);
  const criterion = criterias[critPosition];

  const criterionScore = initialComparison?.criteria_scores.find(
    (crit) => crit.criteria === criterion.name
  );

  const [submittedScore, setSubmittedScore] = useState<number | undefined>(
    undefined
  );

  const onSlideEntered = () => {
    setDisableButtons(false);
    setSlideDirection(slideDirection === 'up' ? 'down' : 'up');
  };

  const onSlideExited = async () => {
    if (slideDirection === 'up') {
      setCritPosition(
        critPosition - 1 >= 0 ? critPosition - 1 : criterias.length - 1
      );
    } else {
      setCritPosition(
        critPosition + 1 < criterias.length ? critPosition + 1 : 0
      );
    }

    setSlideDirection(slideDirection === 'up' ? 'down' : 'up');

    if (submittedScore === undefined) {
      setSlideIn(true);
      return;
    }

    const comparisonRequest = {
      pollName: pollName,
      entity_a: { uid: uidA },
      entity_b: { uid: uidB },
      criteria_scores: [
        {
          criteria: criterion.name,
          score: submittedScore,
          score_max: BUTTON_SCORE_MAX,
        },
      ],
    };

    try {
      await onSubmit(comparisonRequest, true);
    } catch {
      setCritPosition(critPosition);
    } finally {
      setSlideIn(true);
    }
  };

  const moveWithoutPatching = (direction: 'up' | 'down') => {
    if (slideIn === false) {
      return;
    }
    setSlideDirection(direction === 'up' ? 'down' : 'up');
    setSlideIn(false);
    setSubmittedScore(undefined);
  };

  /**
   * FIXME it should not be possible to skip the main criterion if it has not
   * been rated yet.
   */
  const bindDrag = useDrag(
    ({ swipe, type }) => {
      if (slideIn === false) {
        return;
      }

      if (type === 'pointerup' || type === 'touchend') {
        if (swipe[1] < 0) {
          moveWithoutPatching('up');
        } else if (swipe[1] > 0) {
          moveWithoutPatching('down');
        }
      }
    },
    { swipe: { velocity: SWIPE_VELOCITY } }
  );

  const patchScore = async (score: number) => {
    if (slideIn === false) {
      return;
    }
    setSlideDirection('down');
    setSlideIn(false);
    setSubmittedScore(score);
  };

  return (
    <Box width="100%" {...bindDrag()} sx={{ touchAction: 'pan-x' }}>
      <Box display="flex" justifyContent="center">
        <IconButton
          aria-label={t('comparisonCriteriaButtons.previousQualityCriterion')}
          onClick={() => moveWithoutPatching('up')}
        >
          <ArrowDropUp />
        </IconButton>
      </Box>
      <Slide
        in={slideIn}
        appear={false}
        direction={slideDirection}
        onEntered={onSlideEntered}
        onExited={onSlideExited}
        onExiting={() => setDisableButtons(true)}
        timeout={SWIPE_TIMEOUT}
      >
        <ComparisonCriterionButtons
          critName={criterion.name}
          critLabel={criterion.label}
          givenScore={criterionScore?.score}
          disabled={disableButtons}
          onClick={patchScore}
        />
      </Slide>
      <Box display="flex" justifyContent="center">
        <IconButton
          aria-label={t('comparisonCriteriaButtons.nextQualityCriterion')}
          onClick={() => moveWithoutPatching('down')}
        >
          <ArrowDropDown />
        </IconButton>
      </Box>
    </Box>
  );
};

export default ComparisonCriteriaButtons;
