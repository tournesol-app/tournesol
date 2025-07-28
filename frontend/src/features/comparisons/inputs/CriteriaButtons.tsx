import React, { useContext, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDrag } from '@use-gesture/react';
import { Vector2 } from '@use-gesture/core/types';

import { Box, Fade, Slide } from '@mui/material';
import { ArrowDropDown, ArrowDropUp } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks';
import ItemsAreSimilar from 'src/features/comparisons/ItemsAreSimilar';
import { TutorialContext } from 'src/features/comparisonSeries/TutorialContext';

import { ComparisonRequest } from 'src/services/openapi';

import CriterionButtons, { BUTTON_SCORE_MAX } from './CriterionButtons';
import { useOrderedCriteria } from 'src/hooks/useOrderedCriteria';
import { MobileIconButton } from 'src/components/buttons';

const SWIPE_TIMEOUT = 180;
const SWIPE_VELOCITY: number | Vector2 = [0.25, 0.25];

interface CriteriaButtonsProps {
  uidA: string;
  uidB: string;
  initialComparison: ComparisonRequest | null;
  onSubmit: (c: ComparisonRequest, partialUpdate?: boolean) => Promise<void>;
  // Called when a new criterion is displayed.
  onPositionChanged: (pos: number) => void;
}

const removeCriteria = (
  initialComparison: ComparisonRequest,
  submittedCrit: string
) => {
  const index = initialComparison.criteria_scores.findIndex(
    (crit) => crit.criteria === submittedCrit
  );
  if (index !== -1) {
    initialComparison.criteria_scores.splice(index, 1);
  }
  return [...initialComparison.criteria_scores];
};

const CriteriaButtons = ({
  uidA,
  uidB,
  initialComparison,
  onSubmit,
  onPositionChanged,
}: CriteriaButtonsProps) => {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLElement>(null);

  const tutorial = useContext(TutorialContext);
  const { name: pollName, options } = useCurrentPoll();
  const mainCriterionName = options?.mainCriterionName;
  const displayedCriteria = useOrderedCriteria();

  const [slideIn, setSlideIn] = useState(true);
  const [slideDirection, setSlideDirection] = useState<'up' | 'down'>('down');
  const [disableScoreButtons, setDisableScoreButtons] = useState(false);

  const [critPosition, setCritPosition] = useState(0);
  const [submittedScore, setSubmittedScore] = useState<number | undefined>(
    undefined
  );

  const criterion = displayedCriteria[critPosition];
  const criterionScore = initialComparison?.criteria_scores.find(
    (crit) => crit.criteria === criterion.name
  );
  const navigationDisabled =
    tutorial.isActive ||
    (criterion.name === mainCriterionName && criterionScore == undefined);

  const onSlideEntered = () => {
    setDisableScoreButtons(false);
    setSlideDirection(slideDirection === 'up' ? 'down' : 'up');
  };

  const onSlideExited = async () => {
    let nextCritPosition = critPosition;

    // Display only the main criterion during the tutorial.
    if (!tutorial.isActive) {
      if (slideDirection === 'up') {
        nextCritPosition =
          critPosition - 1 >= 0
            ? critPosition - 1
            : displayedCriteria.length - 1;
      } else {
        nextCritPosition =
          critPosition + 1 < displayedCriteria.length ? critPosition + 1 : 0;
      }
    }

    setCritPosition(nextCritPosition);
    setSlideDirection(slideDirection === 'up' ? 'down' : 'up');

    if (submittedScore === undefined) {
      setSlideIn(true);
      onPositionChanged(nextCritPosition);
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
      onPositionChanged(nextCritPosition);
    } catch {
      setCritPosition(critPosition);
    } finally {
      setSlideIn(true);
    }
  };

  const moveWithoutPatching = (direction: 'up' | 'down') => {
    if (slideIn === false || navigationDisabled) {
      return;
    }
    setSlideDirection(direction === 'up' ? 'down' : 'up');
    setSlideIn(false);
    setSubmittedScore(undefined);
  };

  const bindDrag = useDrag(
    ({ swipe, type }) => {
      if (slideIn === false || navigationDisabled) {
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

  const sameScoreGiven = (score: number) => {
    const currentCritScore = initialComparison?.criteria_scores.find(
      (crit) => crit.criteria === criterion.name
    );

    return score === currentCritScore?.score;
  };

  const clearScore = async () => {
    if (
      !initialComparison?.criteria_scores ||
      initialComparison.criteria_scores.length === 0
    ) {
      return;
    }

    const comparisonRequest = {
      pollName: pollName,
      entity_a: { uid: uidA },
      entity_b: { uid: uidB },
      criteria_scores: removeCriteria(initialComparison, criterion.name),
    };

    setDisableScoreButtons(true);
    try {
      await onSubmit(comparisonRequest, false);
    } finally {
      setDisableScoreButtons(false);
    }
  };

  const patchScore = async (score: number) => {
    if (slideIn === false || disableScoreButtons) {
      return;
    }

    if (sameScoreGiven(score)) {
      // Clicking two times on the mandatory main criterion must not clear it
      // score.
      if (criterion.name !== mainCriterionName) {
        clearScore();
      }
    } else {
      setSlideDirection('down');
      setSubmittedScore(score);
      setSlideIn(false);
    }
  };

  if (uidA == uidB) {
    return (
      <Box
        sx={{
          mt: 2,
        }}
      >
        <ItemsAreSimilar />
      </Box>
    );
  }

  return (
    <Box
      ref={containerRef}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        rowGap: 1,
      }}
    >
      <Box
        sx={[
          {
            display: 'flex',
            justifyContent: 'center',
          },
          navigationDisabled
            ? {
                visibility: 'hidden',
              }
            : {
                visibility: 'visible',
              },
        ]}
      >
        <MobileIconButton
          color="secondary"
          aria-label={t('comparisonCriteriaButtons.previousQualityCriterion')}
          onClick={() => moveWithoutPatching('down')}
          disabled={disableScoreButtons || navigationDisabled}
        >
          <ArrowDropUp />
        </MobileIconButton>
      </Box>
      <Slide
        in={slideIn}
        appear={false}
        direction={slideDirection}
        onEntered={onSlideEntered}
        onExited={onSlideExited}
        onExiting={() => setDisableScoreButtons(true)}
        timeout={SWIPE_TIMEOUT}
        container={containerRef.current}
      >
        {/* A div is required between Slide and Fade to prevent them from
            cancelling each other transition. */}
        <div>
          <Fade in={slideIn} appear={true} timeout={SWIPE_TIMEOUT}>
            <Box
              {...bindDrag()}
              sx={[
                {
                  touchAction: 'none',
                },
                disableScoreButtons
                  ? {
                      pointerEvents: 'none',
                    }
                  : {
                      pointerEvents: null,
                    },
              ]}
            >
              <CriterionButtons
                critName={criterion.name}
                critLabel={criterion.label}
                givenScore={criterionScore?.score}
                disabled={disableScoreButtons}
                onClick={patchScore}
              />
            </Box>
          </Fade>
        </div>
      </Slide>
      <Box
        sx={[
          {
            display: 'flex',
            justifyContent: 'center',
          },
          navigationDisabled
            ? {
                visibility: 'hidden',
              }
            : {
                visibility: 'visible',
              },
        ]}
      >
        <MobileIconButton
          color="secondary"
          aria-label={t('comparisonCriteriaButtons.nextQualityCriterion')}
          onClick={() => moveWithoutPatching('up')}
          disabled={disableScoreButtons || navigationDisabled}
        >
          <ArrowDropDown />
        </MobileIconButton>
      </Box>
    </Box>
  );
};

export default CriteriaButtons;
