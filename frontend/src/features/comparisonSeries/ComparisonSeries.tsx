import React, { useEffect, useState } from 'react';
import { StepLabel, Step, Stepper, Container } from '@mui/material';
import Comparison from 'src/features/comparisons/Comparison';
import { Entity } from 'src/services/openapi';

const MIN_LENGTH = 2;

interface Props {
  getAlternatives?: () => Promise<Array<Entity>>;
  length: number;
  messages: string;
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

const selectNextEntity = (entities: Array<Entity>): Entity => {
  return entities[Math.floor(Math.random() * entities.length)];
};

const ComparisonSeries = ({ getAlternatives, length, messages }: Props) => {
  // the current position in the series
  const [step, setStep] = useState(0);
  // tell the `Comparison` to refresh the left entity, or the right one
  const [refreshLeft, setRefreshLeft] = useState(false);
  // a limited list of entities that can be used to suggest new comparisons
  const [alternatives, setAlternatives] = useState<Array<Entity>>([]);

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

  const afterSubmitCallback = (): { uid: string; refreshLeft: boolean } => {
    if (step < length) {
      setStep(step + 1);
    }

    let uid = '';
    if (alternatives.length > 0) {
      uid = selectNextEntity(alternatives).uid;
    }

    const nextStep = { uid: uid, refreshLeft: refreshLeft };
    setRefreshLeft(!refreshLeft);

    return nextStep;
  };

  return (
    <>
      {length >= MIN_LENGTH ? (
        <>
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
