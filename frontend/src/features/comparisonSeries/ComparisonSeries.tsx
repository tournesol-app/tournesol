import React, { useState } from 'react';
import { StepLabel, Step, Stepper, Container } from '@mui/material';
import Comparison from 'src/features/comparisons/Comparison';

const MIN_LENGTH = 2;

interface Props {
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

const ComparisonSeries = ({ length, messages }: Props) => {
  const [step, setStep] = useState(0);

  const afterSubmitCallback = () => {
    if (step < length) {
      setStep(step + 1);
    }
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
