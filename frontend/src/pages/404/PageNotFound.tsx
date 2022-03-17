import React from 'react';
import { Box, Typography } from '@mui/material';

const PageNotFound = () => {
  return (
    <Box
      height="100%"
      sx={{
        backgroundImage: "url('/svg/backgrounds/chandelier.svg')",
        backgroundPosition: 'center',
        backgroundRepeatY: 'no-repeat',
      }}
    >
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        textAlign="center"
        py={26}
      >
        <Typography variant="h2">Sorry, page not found.</Typography>
        <Typography variant="subtitle1">
          Please check if the requested address is correct.
        </Typography>
      </Box>
    </Box>
  );
};

export default PageNotFound;
