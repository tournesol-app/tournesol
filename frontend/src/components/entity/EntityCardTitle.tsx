import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { Box, Typography } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';

const EntityCardTitle = ({
  uid,
  title,
  compact = true,
  titleMaxLines = 3,
  withLink = true,
  ...rest
}: {
  uid: string;
  title: string;
  compact?: boolean;
  titleMaxLines?: number;
  withLink?: boolean;
  [propName: string]: unknown;
}) => {
  const { baseUrl } = useCurrentPoll();

  const titleNode = (
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
  );

  return (
    <Box display="flex" flexWrap="wrap">
      {withLink ? (
        <RouterLink className="no-decoration" to={`${baseUrl}/entities/${uid}`}>
          {titleNode}
        </RouterLink>
      ) : (
        titleNode
      )}
    </Box>
  );
};

export default EntityCardTitle;
