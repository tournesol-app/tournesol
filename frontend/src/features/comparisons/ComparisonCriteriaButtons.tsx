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
  onSubmit: (c: ComparisonRequest, partialUpdate?: boolean) => Promise<void>;
}

const ComparisonCriteriaButtons = ({
  uidA,
  uidB,
  onSubmit,
}: ComparisonCriteriaButtonsProps) => {
  const { criterias, name: pollName } = useCurrentPoll();

  const [slideIn, setSlideIn] = useState(true);
  const [slideDirection, setSlideDirection] = useState<'up' | 'down'>('down');
  const [currentCrit, setCurrentCrit] = useState(0);

  const criterion = criterias[currentCrit];

  const slide = () => {
    if (slideIn === false) {
      return;
    }
    setSlideIn(false);
  };

  const onSlideEntered = () => {
    setSlideDirection('down');
  };

  const onSlideExited = () => {
    setSlideDirection('up');

    if (currentCrit + 1 < criterias.length) {
      setCurrentCrit(currentCrit + 1);
    } else {
      setCurrentCrit(0);
    }

    setSlideIn(true);
  };

  const bindDrag = useDrag(
    ({ swipe, type }) => {
      if (slideIn === false) {
        return;
      }

      if (type === 'pointerup' || type === 'touchend') {
        if (swipe[1] < 0) {
          slide();
        }
      }
    },
    { swipe: { velocity: SWIPE_VELOCITY } }
  );

  const onClick = async (criterion: string, score: number) => {
    const comparisonRequest = {
      pollName: pollName,
      entity_a: { uid: uidA },
      entity_b: { uid: uidB },
      criteria_scores: [
        {
          criteria: criterion,
          score: score,
        },
      ],
    };

    try {
      await onSubmit(comparisonRequest, true);
      slide();
    } catch {
      // XXX handle error
    }
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
          onClick={onClick}
        />
      </Slide>
    </Box>
  );
};

export default ComparisonCriteriaButtons;
