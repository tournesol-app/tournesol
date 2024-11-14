import React from 'react';
import { Button, ButtonProps } from '@mui/material';

const MobileButton = (props: ButtonProps) => {
  return (
    <Button
      {...props}
      sx={{
        ...props.sx,
        bgcolor: 'background.mobileButton',
        '&:hover': {
          bgcolor: 'background.mobileButton',
        },
      }}
    />
  );
};

export default MobileButton;
