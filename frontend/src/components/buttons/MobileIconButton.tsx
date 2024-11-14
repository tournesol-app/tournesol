import React from 'react';
import { IconButton, IconButtonProps } from '@mui/material';

const MobileIconButton = (props: IconButtonProps) => {
  return (
    <IconButton
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

export default MobileIconButton;
