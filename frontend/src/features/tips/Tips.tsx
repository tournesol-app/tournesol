import React, { useEffect, useState } from 'react';

import { Box, Grid, IconButton } from '@mui/material';
import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';

import { OrderedDialogs } from 'src/utils/types';

import Tip from './Tip';

interface TipsProps {
  // Display the tip located at `dialogs[step]`.
  step: number;
  // Stop displaying automatically `dialogs[step]` when
  // `step` >= `stopAutoDisplay`. The user can still browse the previous tips.
  stopAutoDisplay: number;
  content?: OrderedDialogs;
}

const Tips = ({ step, content, stopAutoDisplay }: TipsProps) => {
  const [index, setIndex] = useState(Math.min(stopAutoDisplay - 1, step));

  useEffect(() => {
    setIndex(Math.min(stopAutoDisplay - 1, step));
  }, [step, stopAutoDisplay]);

  const previousTip = () => {
    setIndex(index - 1);
  };

  const nextTip = () => {
    setIndex(index + 1);
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
        <Box display="flex" justifyContent="center">
          <IconButton onClick={previousTip} disabled={index <= 0}>
            <KeyboardArrowLeft fontSize="large" />
          </IconButton>
        </Box>
      </Grid>
      <Grid item maxWidth="880px">
        {content && <Tip tip={content[index]} />}
      </Grid>
      <Grid item xs={1}>
        <Box display="flex" justifyContent="center">
          <IconButton
            onClick={nextTip}
            disabled={index >= step || index >= stopAutoDisplay - 1}
          >
            <KeyboardArrowRight fontSize="large" />
          </IconButton>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Tips;
