import React, { useEffect, useState } from 'react';

import { Box, Grid, IconButton } from '@mui/material';
import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';

import { OrderedDialogs } from 'src/utils/types';

import Tip from './Tip';

interface TipsProps {
  // Display the tip located at `content[step]`.
  step: number;
  // Stop displaying automatically `content[step]` when
  // `step` >= `stopAutoDisplay`. The user can still browse the previous tips.
  stopAutoDisplay: number;
  content?: OrderedDialogs;
  tipWidth?: number;
}

const Tips = ({
  step,
  stopAutoDisplay,
  content,
  tipWidth = 880,
}: TipsProps) => {
  const [index, setIndex] = useState(Math.min(stopAutoDisplay - 1, step));

  useEffect(() => {
    setIndex(Math.min(stopAutoDisplay - 1, step));
  }, [step, stopAutoDisplay]);

  const previousTip = () => setIndex(index - 1);

  const nextTip = () => setIndex(index + 1);

  const disablePrev = () => {
    return index <= 0;
  };

  const disableNext = () => {
    return index >= step || index >= stopAutoDisplay - 1;
  };

  if (!content) {
    return <></>;
  }

  return (
    <Grid
      container
      direction="row"
      justifyContent="center"
      alignItems="flex-start"
      flexWrap="nowrap"
      mb={2}
    >
      <Grid item xs={1}>
        <Box
          display="flex"
          justifyContent="center"
          visibility={disablePrev() ? 'hidden' : 'visible'}
        >
          <IconButton
            color="secondary"
            onClick={previousTip}
            disabled={disablePrev()}
            data-testid="tips-prev"
          >
            <KeyboardArrowLeft fontSize="large" />
          </IconButton>
        </Box>
      </Grid>
      <Grid item width={`${tipWidth}px`}>
        {content && <Tip tip={content[index]} tipId={step.toString()} />}
      </Grid>
      <Grid item xs={1}>
        <Box
          display="flex"
          justifyContent="center"
          visibility={disableNext() ? 'hidden' : 'visible'}
        >
          <IconButton
            color="secondary"
            onClick={nextTip}
            disabled={disableNext()}
            data-testid="tips-next"
          >
            <KeyboardArrowRight fontSize="large" />
          </IconButton>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Tips;
