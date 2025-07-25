import React from 'react';

import { Box, Divider, SxProps, Typography, useTheme } from '@mui/material';

interface SectionTitleProps {
  title: string;
  color?: string;
  dividerColor?: string;
  headingId?: string;
}

/**
 * A title of an home page section.
 */
const SectionTitle = ({
  title,
  color,
  dividerColor,
  headingId,
}: SectionTitleProps) => {
  const theme = useTheme();

  let sx: SxProps = { width: '100%' };

  if (dividerColor) {
    sx = { ...sx, '&::before, &::after': { borderColor: dividerColor } };
  }

  return (
    <Box
      my={6}
      width="100%"
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <Divider component="div" role="presentation" sx={sx}>
        <Typography
          id={headingId}
          variant="h1"
          component="h2"
          textAlign="center"
          color={color || theme.palette.text.primary}
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
