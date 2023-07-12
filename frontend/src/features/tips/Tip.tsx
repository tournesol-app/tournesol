import React from 'react';

import { Alert, AlertTitle } from '@mui/material';

interface TipSingleProps {
  tip: { title: string; message: string };
}

const Tip = ({ tip }: TipSingleProps) => {
  return (
    <Alert severity="info">
      <AlertTitle>
        <strong>{tip.title}</strong>
      </AlertTitle>
      {tip.message.repeat(20)}
    </Alert>
  );
};

export default Tip;
