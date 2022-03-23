import React, { useEffect, useState } from 'react';
import { StepLabel, Step, Stepper, Container } from '@mui/material';
import Comparison from 'src/features/comparisons/Comparison';
import { Entity } from 'src/services/openapi';
import DialogBox from './DialogBox';

const MIN_LENGTH = 2;
const COMPARISON_SEPARATOR = '/';

interface Props {
  dialogs?: { [key: string]: { title: string; messages: Array<string> } };
  getAlternatives?: () => Promise<Array<Entity>>;
  length: number;
}

const generateSteps = (length: number) => {
  const content = [];
  for (let i = 0; i < length; i++) {
    content.push(
      <Step key={i}>
        <StepLabel>
          {i === 0 && 'begin'}
          {i === length - 1 && 'finish!'}
        </StepLabel>
      </Step>
    );
  }
  return content;
};

/**
 * Return a random entity with uid not included in the `filter` list.
 *
 * @param entities
 * @param filter
 */
const selectNextEntity = (
  entities: Array<Entity>,
  filter: string[]
): Entity => {
  const filtered = entities.filter((entity) => !filter.includes(entity.uid));

  return filtered[Math.floor(Math.random() * filtered.length)];
};

/**
 * Return a list of uids already compared with `uid`.
 *
 * @param uid
 * @param comparisons An array of comparisons, represented in the form 'uidA/uidB'
 */
const alreadyComparedWith = (uid: string, comparisons: string[]): string[] => {
  const alreadyCompared: Array<string> = [];

  comparisons.forEach((comparison) => {
    const split = comparison.split(COMPARISON_SEPARATOR);
    const index = split.indexOf(uid);

    if (index != -1) {
      if (index == 0) {
        alreadyCompared.push(split[1]);
      } else {
        alreadyCompared.push(split[0]);
      }
    }
  });

  return alreadyCompared;
};

const ComparisonSeries = ({ getAlternatives, length, dialogs }: Props) => {
  // the current position in the series
  const [step, setStep] = useState(0);
  // state of the `Dialog` component
  const [dialogOpen, setDialogOpen] = useState(true);
  // tell the `Comparison` to refresh the left entity, or the right one
  const [refreshLeft, setRefreshLeft] = useState(false);
  // a limited list of entities that can be used to suggest new comparisons
  const [alternatives, setAlternatives] = useState<Array<Entity>>([]);
  // a list of already made comparisons, allowing to not suggest two times the
  // same comparison to a user
  const [comparisonsMade, setComparisonsMade] = useState<Array<string>>([]);

  /**
   * Build the list of `alternatives`.
   *
   * After each comparison, an entity from this list can be selected to
   * replace one of the two compared entities.
   */
  useEffect(() => {
    async function getAlternativesAsync() {
      if (getAlternatives) {
        const alts = await getAlternatives();
        if (alts.length > 0) {
          setAlternatives(alts);
        }
      }
    }

    getAlternativesAsync();
  }, [getAlternatives]);

  const afterSubmitCallback = (
    uidA: string,
    uidB: string
  ): { uid: string; refreshLeft: boolean } => {
    const newStep = step + 1;

    if (step < length) {
      setStep(newStep);
    }

    const newComparisons = comparisonsMade.concat([
      uidA + COMPARISON_SEPARATOR + uidB,
    ]);
    setComparisonsMade(newComparisons);

    const keptUid = refreshLeft ? uidB : uidA;
    const alreadyCompared = alreadyComparedWith(keptUid, newComparisons);

    let uid = '';
    if (alternatives.length > 0) {
      uid = selectNextEntity(
        alternatives,
        alreadyCompared.concat([keptUid])
      ).uid;
    }

    const nextStep = { uid: uid, refreshLeft: refreshLeft };
    setRefreshLeft(!refreshLeft);

    if (dialogs && newStep in dialogs) {
      setDialogOpen(true);
    }

    return nextStep;
  };

  const closeDialog = () => {
    setDialogOpen(false);
  };

  return (
    <>
      {length >= MIN_LENGTH ? (
        <>
          {dialogs && step in dialogs && (
            <DialogBox
              dialog={dialogs[step]}
              open={dialogOpen}
              onClose={closeDialog}
            />
          )}
          <Container maxWidth="md" sx={{ my: 2, mb: 4 }}>
            <Stepper activeStep={step} alternativeLabel>
              {generateSteps(length)}
            </Stepper>
          </Container>
          <Comparison afterSubmitCallback={afterSubmitCallback} />
        </>
      ) : (
        <Comparison />
      )}
    </>
  );
};

export default ComparisonSeries;
