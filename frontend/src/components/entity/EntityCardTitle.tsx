import React from 'react';
import { Box, Typography } from '@mui/material';

const EntityCardTitle = ({
  title,
  compact = true,
  titleMaxLines = 3,
  ...rest
}: {
  title: string;
  compact?: boolean;
  titleMaxLines?: number;
  [propName: string]: unknown;
}) => {
  return (
    <Box display="flex" flexWrap="wrap">
      <Typography
        sx={{
          fontSize: compact ? '1em !important' : '',
          lineHeight: 1.3,
          textAlign: 'left',
          // Limit text to 3 lines and show ellipsis
          display: '-webkit-box',
          overflow: 'hidden',
          WebkitLineClamp: titleMaxLines,
          WebkitBoxOrient: 'vertical',
        }}
        variant={compact ? 'body1' : 'h6'}
        title={title}
        {...rest}
      >
        {title}
      </Typography>
    </Box>
  );
};

export default EntityCardTitle;
