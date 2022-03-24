import React, { useEffect, useRef, useState } from 'react';
import { Redirect } from 'react-router-dom';
import { StepLabel, Step, Stepper, Container } from '@mui/material';
import DialogBox from 'src/components/DialogBox';
import Comparison, { UID_PARAMS } from 'src/features/comparisons/Comparison';
import { Entity } from 'src/services/openapi';
import { alreadyComparedWith, selectRandomEntity } from 'src/utils/entity';
import { OrderedDialogs } from 'src/utils/types';

const MIN_LENGTH = 2;

interface Props {
  dialogs?: OrderedDialogs;
  generateInitial?: boolean;
  getAlternatives?: () => Promise<Array<Entity>>;
  length: number;
}

const generateSteps = (length: number) => {
  const content = [];
  for (let i = 0; i < length; i++) {
    content.push(
      <Step key={i}>
        <StepLabel>
          {i === 0 && 'start'}
          {i === length - 1 && 'end!'}
        </StepLabel>
      </Step>
    );
  }
  return content;
};

const ComparisonSeries = ({
  generateInitial,
  getAlternatives,
  length,
  dialogs,
}: Props) => {
  // trigger the initialization on the first render only, to allow users to
  // freely clear entities without being redirected
  const initialize = useRef(
    generateInitial != undefined ? generateInitial : false
  );
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

  const searchParams = new URLSearchParams(location.search);
  const uidA: string = searchParams.get(UID_PARAMS.vidA) || '';
  const uidB: string = searchParams.get(UID_PARAMS.vidB) || '';

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

    const newComparisons = comparisonsMade.concat([uidA + '/' + uidB]);
    setComparisonsMade(newComparisons);

    const keptUid = refreshLeft ? uidB : uidA;
    const alreadyCompared = alreadyComparedWith(keptUid, newComparisons);

    let uid = '';
    if (alternatives.length > 0) {
      uid = selectRandomEntity(
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

  const genInitialComparisonParams = (
    from: Array<Entity>,
    uidA: string,
    uidB: string
  ): string => {
    if (from.length === 0) {
      return '';
    }

    const newSearchParams = new URLSearchParams();
    newSearchParams.append('series', 'true');

    let randomA = '';
    let randomB = '';

    if (uidA === '') {
      randomA = selectRandomEntity(from, []).uid;
      newSearchParams.append(UID_PARAMS.vidA, randomA);
    } else {
      newSearchParams.append(UID_PARAMS.vidA, uidA);
    }

    if (uidB === '') {
      randomB = selectRandomEntity(from, [randomA]).uid;
      newSearchParams.append(UID_PARAMS.vidB, randomB);
    } else {
      newSearchParams.append(UID_PARAMS.vidB, uidB);
    }

    return newSearchParams.toString();
  };

  if (initialize.current == true && uidA !== '' && uidB !== '') {
    initialize.current = false;
  }

  if (initialize.current == true && (uidA === '' || uidB === '')) {
    if (alternatives.length > 0) {
      const initialParams = genInitialComparisonParams(
        alternatives,
        uidA,
        uidB
      );

      return (
        <Redirect to={{ pathname: location.pathname, search: initialParams }} />
      );
    }
  }

  return (
    <>
      {length >= MIN_LENGTH ? (
        <>
          {/*
            Do not display the dialog box while the alternatives array
            is being built, to avoid a blink effect.
          */}
          {dialogs &&
            step in dialogs &&
            (!getAlternatives || alternatives.length > 0) && (
              <DialogBox
                dialog={dialogs[step]}
                open={dialogOpen}
                onClose={closeDialog}
              />
            )}
          <Container maxWidth="md" sx={{ my: 2 }}>
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
