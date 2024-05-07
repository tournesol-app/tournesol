import React, { useState } from 'react';
import { useDrag } from '@use-gesture/react';
import { Vector2 } from '@use-gesture/core/types';

import { Box, Slide } from '@mui/material';

import ComparisonCriterionButtons from 'src/features/comparisons/ComparisonCriterionButtons';
import { useCurrentPoll } from 'src/hooks';
import { ComparisonRequest } from 'src/services/openapi';

const SWIPE_TIMEOUT = 225;
const SWIPE_VELOCITY: number | Vector2 = [0.35, 0.35];

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
  const { criterias, name: pollName } = useCurrentPoll();

  const [slideIn, setSlideIn] = useState(true);
  const [slideDirection, setSlideDirection] = useState<'up' | 'down'>('down');

  const [critPosition, setCritPosition] = useState(0);
  const criterion = criterias[critPosition];

  const criterionScore = initialComparison?.criteria_scores.find(
    (crit) => crit.criteria === criterion.name
  );

  const [submittedScore, setSubmittedScore] = useState<number | undefined>(
    undefined
  );

  const onSlideEntered = () => {
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
          // TODO: create a constant
          score_max: 2,
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

  const moveWithoutPatching = (from: 'up' | 'down') => {
    if (slideIn === false) {
      return;
    }
    setSlideDirection(from);
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
        // Swipe up
        if (swipe[1] < 0) {
          moveWithoutPatching('down');
          // Swipe down
        } else if (swipe[1] > 0) {
          moveWithoutPatching('up');
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
      <Slide
        in={slideIn}
        appear={false}
        direction={slideDirection}
        onEntered={onSlideEntered}
        onExited={onSlideExited}
        timeout={SWIPE_TIMEOUT}
      >
        <ComparisonCriterionButtons
          critName={criterion.name}
          critLabel={criterion.label}
          givenScore={criterionScore?.score}
          onClick={patchScore}
        />
      </Slide>
    </Box>
  );
};

export default ComparisonCriteriaButtons;
