import React, { useEffect, useState } from 'react';

import Tip from './Tip';
import { Grid, IconButton } from '@mui/material';
import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';

interface TipsProps {
  step: number;
}

const Tips = ({ step }: TipsProps) => {
  const tipList = [
    { title: 'Important tip1 title !', message: 'tip1 text' },
    { title: 'Important tip2 title !', message: 'tip2 text' },
    { title: 'Important tip3 title !', message: 'tip3 text' },
    { title: 'Important tip4 title !', message: 'tip4 text' },
  ];

  const [tipStep, setTipStep] = useState(step);
  useEffect(() => {
    const retrieveStep = () => {
      setTipStep(step);
    };
    retrieveStep();
  }, [step]);

  const handlePreviousTip = () => {
    setTipStep(tipStep - 1);
  };

  const handleNextTip = () => {
    setTipStep(tipStep + 1);
  };

  return (
    <Grid
      container
      sx={{ maxWidth: '880px' }}
      direction="row"
      justifyContent="center"
      alignItems="center"
    >
      <Grid item>
        <IconButton onClick={handlePreviousTip} disabled={!(tipStep > 0)}>
          <KeyboardArrowLeft />
        </IconButton>
      </Grid>
      <Grid item xs={10}>
        <Tip tip={tipList[tipStep]} />
      </Grid>
      <Grid item>
        <IconButton
          onClick={handleNextTip}
          disabled={!(tipStep < step && tipStep < tipList.length - 1)}
        >
          <KeyboardArrowRight />
        </IconButton>
      </Grid>
    </Grid>
  );
};

export default Tips;
