import React from 'react';

import { Alert, AlertTitle, Grid } from '@mui/material';

interface TipSingleProps {
  tip: string;
}

const Tip = ({ tip }: TipSingleProps) => {
  return (
    <Grid container sx={{ maxWidth: '880px' }}>
      <Alert severity="info">
        <AlertTitle>
          <strong>Important tip title !</strong>
        </AlertTitle>
        {tip.repeat(20)}
      </Alert>
    </Grid>
  );
};

export default Tip;
