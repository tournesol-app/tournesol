import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { Box, Typography } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';

const EntityCardTitle = ({
  uid,
  title,
  compact = true,
  titleMaxLines = 3,
  ...rest
}: {
  uid: string;
  title: string;
  compact?: boolean;
  titleMaxLines?: number;
  [propName: string]: unknown;
}) => {
  const { baseUrl } = useCurrentPoll();

  return (
    <Box display="flex" flexWrap="wrap">
      <RouterLink className="no-decoration" to={`${baseUrl}/entities/${uid}`}>
        <Typography
          color="text.primary"
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
      </RouterLink>
    </Box>
  );
};

export default EntityCardTitle;
