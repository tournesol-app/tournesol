import React, { useEffect, useState } from 'react';

import Tip from './Tip';
import { Box, Grid, IconButton } from '@mui/material';
import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';
import { OrderedDialogs } from 'src/utils/types';

interface TipsProps {
  step: number;
  dialogs: OrderedDialogs | undefined;
  tutorialLength: number;
}

const Tips = ({ step, dialogs, tutorialLength }: TipsProps) => {
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
      alignItems="flex-start"
      mb={2}
    >
      <Grid item xs={1}>
        <Box display="flex" justifyContent="center">
          <IconButton onClick={handlePreviousTip} disabled={!(tipStep > 0)}>
            <KeyboardArrowLeft />
          </IconButton>
        </Box>
      </Grid>
      <Grid item xs={10}>
        {dialogs && <Tip tip={dialogs[tipStep]} />}
      </Grid>
      <Grid item xs={1}>
        <Box display="flex" justifyContent="center">
          <IconButton
            onClick={handleNextTip}
            disabled={!(tipStep < step && tipStep < tutorialLength - 1)}
          >
            <KeyboardArrowRight />
          </IconButton>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Tips;
