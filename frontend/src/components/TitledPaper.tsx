import React from 'react';

import { Box, Paper, Typography, SxProps } from '@mui/material';

interface TitledPaperProps {
  title: string;
  titleId?: string;
  children: React.ReactNode;
  sx?: SxProps;
  contentBoxPadding?: number;
}

/**
 * A reusable MUI <Paper> with a customized header and a padded content.
 */
const TitledPaper = ({
  title,
  titleId,
  children,
  sx,
  contentBoxPadding = 2,
}: TitledPaperProps) => {
  return (
    <Paper sx={sx}>
      <Box
        p={2}
        color="#fff"
        bgcolor="background.emphatic"
        sx={{
          borderTopLeftRadius: 'inherit',
          borderTopRightRadius: 'inherit',
        }}
      >
        <Typography variant="h4" id={titleId}>
          {title}
        </Typography>
      </Box>
      <Box p={contentBoxPadding}>{children}</Box>
    </Paper>
  );
};

export default TitledPaper;
