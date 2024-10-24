import React from 'react';

import { Typography } from '@mui/material';

interface SettingsHeadingProps {
  id: string;
  text: string;
}

const SettingsHeading = ({ id, text }: SettingsHeadingProps) => {
  return (
    <Typography
      id={id}
      variant="h5"
      sx={(theme) => ({
        textDecorationLine: 'underline',
        textDecorationColor: theme.palette.primary.main,
        textDecorationThickness: '0.2em',
        textDecorationSkipInk: 'none',
        textUnderlineOffset: '0.1em',
      })}
    >
      {text}
    </Typography>
  );
};

export default SettingsHeading;
