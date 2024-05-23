import React, { useContext, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useDrag } from '@use-gesture/react';
import { Vector2 } from '@use-gesture/core/types';

import { Box, IconButton, Slide } from '@mui/material';
import { ArrowDropDown, ArrowDropUp } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks';
import { TutorialContext } from 'src/features/comparisonSeries/TutorialContext';
import { selectSettings } from 'src/features/settings/userSettingsSlice';

import { ComparisonRequest } from 'src/services/openapi';

import CriterionButtons, { BUTTON_SCORE_MAX } from './CriterionButtons';

const SWIPE_TIMEOUT = 225;
const SWIPE_VELOCITY: number | Vector2 = [0.25, 0.25];

interface CriteriaButtonsProps {
  uidA: string;
  uidB: string;
  initialComparison: ComparisonRequest | null;
  onSubmit: (c: ComparisonRequest, partialUpdate?: boolean) => Promise<void>;
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
}: CriteriaButtonsProps) => {
  const { t } = useTranslation();
  const tutorial = useContext(TutorialContext);

  const { criterias: pollCriteria, name: pollName, options } = useCurrentPoll();
  const mainCriterionName = options?.mainCriterionName;

  const userSettings = useSelector(selectSettings)?.settings;
  const orderedByPreferences = userSettings.videos?.comparison__criteria_order;

  // Order the displayed criteria according to the user's preferences.
  const displayedCriteria = useMemo(() => {
    const remainingCriteria = [...pollCriteria];
    const results = [remainingCriteria[0]];
    remainingCriteria.shift();

    if (orderedByPreferences != undefined) {
      orderedByPreferences.forEach((critName) => {
        const found = remainingCriteria.findIndex(
          (pollCrit) => pollCrit.name === critName
        );

        if (found !== -1) {
          results.push(remainingCriteria.splice(found, 1)[0]);
        }
      });
    }

    return results.concat(remainingCriteria);
  }, [orderedByPreferences, pollCriteria]);

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
          critPosition - 1 >= 0 ? critPosition - 1 : pollCriteria.length - 1;
      } else {
        nextCritPosition =
          critPosition + 1 < pollCriteria.length ? critPosition + 1 : 0;
      }
    }

    setCritPosition(nextCritPosition);
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

    if (sameScoreGiven(score) && criterion.name !== mainCriterionName) {
      clearScore();
    } else {
      setSlideDirection('down');
      setSubmittedScore(score);
      setSlideIn(false);
    }
  };

  return (
    <Box display="flex" flexDirection="column" rowGap={1}>
      {!navigationDisabled && (
        <Box display="flex" justifyContent="center">
          <IconButton
            aria-label={t('comparisonCriteriaButtons.nextQualityCriterion')}
            onClick={() => moveWithoutPatching('down')}
            disabled={disableScoreButtons}
          >
            <ArrowDropUp />
          </IconButton>
        </Box>
      )}
      <Slide
        in={slideIn}
        appear={false}
        direction={slideDirection}
        onEntered={onSlideEntered}
        onExited={onSlideExited}
        onExiting={() => setDisableScoreButtons(true)}
        timeout={SWIPE_TIMEOUT}
      >
        <Box {...bindDrag()} sx={{ touchAction: 'pan-x' }}>
          <CriterionButtons
            critName={criterion.name}
            critLabel={criterion.label}
            givenScore={criterionScore?.score}
            disabled={disableScoreButtons}
            onClick={patchScore}
          />
        </Box>
      </Slide>
      {!navigationDisabled && (
        <Box display="flex" justifyContent="center">
          <IconButton
            aria-label={t('comparisonCriteriaButtons.previousQualityCriterion')}
            onClick={() => moveWithoutPatching('up')}
            disabled={disableScoreButtons}
          >
            <ArrowDropDown />
          </IconButton>
        </Box>
      )}
    </Box>
  );
};

export default CriteriaButtons;