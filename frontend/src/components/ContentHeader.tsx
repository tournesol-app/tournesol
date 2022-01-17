import React from 'react';
import { Box, Typography } from '@mui/material';

const ContentHeader = ({ title }: { title: string }) => {
  return (
    <Box
      px={[2, 4]}
      py={2}
      color="text.secondary"
      bgcolor="background.menu"
      borderBottom="1px solid rgba(0, 0, 0, 0.12)"
    >
      <Typography variant="h4">{title}</Typography>
    </Box>
  );
};

export default ContentHeader;
