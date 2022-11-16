import React from 'react';

import { Box, Divider, SxProps, Typography } from '@mui/material';

interface SectionTitleProps {
  title: string;
  dividerColor?: string;
}

/**
 * A title of an home page section.
 */
const SectionTitle = ({ title, dividerColor }: SectionTitleProps) => {
  let sx: SxProps = {
    width: { xs: '100%', lg: '75%' },
  };

  if (dividerColor) {
    sx = { ...sx, '&::before, &::after': { borderColor: dividerColor } };
  }

  return (
    <Box
      mb={6}
      width="100%"
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <Divider component="div" role="presentation" sx={sx}>
        <Typography
          variant="h1"
          component="h2"
          textAlign="center"
          pl={4}
          pr={4}
        >
          {title}
        </Typography>
      </Divider>
    </Box>
  );
};

export default SectionTitle;
