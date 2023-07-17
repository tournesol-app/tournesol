import React, { useEffect, useState } from 'react';

import Tip from './Tip';
import { Box, Grid, IconButton } from '@mui/material';
import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';
import { OrderedDialogs } from 'src/utils/types';

interface TipsProps {
  comparisonsCount: number;
  dialogs: OrderedDialogs | undefined;
  maxIndex: number;
}

const Tips = ({ comparisonsCount, dialogs, maxIndex }: TipsProps) => {
  const [index, setIndex] = useState(Math.min(maxIndex - 1, comparisonsCount));

  useEffect(() => {
    setIndex(Math.min(maxIndex - 1, comparisonsCount));
  }, [comparisonsCount, maxIndex]);

  const handlePreviousTip = () => {
    setIndex(index - 1);
  };

  const handleNextTip = () => {
    setIndex(index + 1);
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
          <IconButton onClick={handlePreviousTip} disabled={!(index > 0)}>
            <KeyboardArrowLeft />
          </IconButton>
        </Box>
      </Grid>
      <Grid item xs={10}>
        {dialogs && <Tip tip={dialogs[index]} />}
      </Grid>
      <Grid item xs={1}>
        <Box display="flex" justifyContent="center">
          <IconButton
            onClick={handleNextTip}
            disabled={!(index < comparisonsCount && index < maxIndex - 1)}
          >
            <KeyboardArrowRight />
          </IconButton>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Tips;
