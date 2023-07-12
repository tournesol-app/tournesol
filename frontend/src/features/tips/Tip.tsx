import React from 'react';

import { Alert, AlertTitle, Typography } from '@mui/material';

interface TipSingleProps {
  tip: { title: string; messages: string[] };
}

const Tip = ({ tip }: TipSingleProps) => {
  return (
    <Alert severity="info">
      <AlertTitle>
        <strong>{tip.title}</strong>
      </AlertTitle>
      {tip.messages.map((message, index) => {
        return (
          <Typography key={index} paragraph>
            {message}
          </Typography>
        );
      })}
    </Alert>
  );
};

export default Tip;
