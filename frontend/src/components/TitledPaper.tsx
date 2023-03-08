import React from 'react';

import { Box, Paper, Typography, SxProps } from '@mui/material';

interface TitledPaperProps {
  title: React.ReactNode;
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
        id={titleId}
        p={2}
        color="#fff"
        bgcolor="background.emphatic"
        sx={{
          borderTopLeftRadius: 'inherit',
          borderTopRightRadius: 'inherit',
        }}
      >
        {typeof title === 'string' ? (
          <Typography variant="h4">{title}</Typography>
        ) : (
          title
        )}
      </Box>
      <Box p={contentBoxPadding}>{children}</Box>
    </Paper>
  );
};

export default TitledPaper;
