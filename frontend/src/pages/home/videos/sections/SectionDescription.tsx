import React from 'react';

import { Box, Typography, useTheme } from '@mui/material';

interface SectionDescriptionProps {
  description: string;
  color?: string;
}

const SectionDescription = ({
  description,
  color,
}: SectionDescriptionProps) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        my: 4,
      }}
    >
      <Box sx={{ width: { lg: '66%', xl: '66%' } }}>
        <Typography
          variant="h3"
          sx={{
            textAlign: 'center',
            letterSpacing: '0.8px',
          }}
          color={color || theme.palette.text.primary}
        >
          {description}
        </Typography>
      </Box>
    </Box>
  );
};

export default SectionDescription;
