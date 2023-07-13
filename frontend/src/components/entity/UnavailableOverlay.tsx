import React from 'react';

import { Box, Typography, useTheme } from '@mui/material';

const UnavailableOverlay = ({ msg }: { msg: string }) => {
  const theme = useTheme();

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      position="absolute"
      top="0"
      color="white"
      bgcolor="rgba(0,0,0,.6)"
      width="100%"
      sx={{
        aspectRatio: '16/9',
        [theme.breakpoints.down('sm')]: {
          fontSize: '0.6rem',
        },
      }}
    >
      <Typography textAlign="center" fontSize="inherit">
        {msg}
      </Typography>
    </Box>
  );
};

export default UnavailableOverlay;
