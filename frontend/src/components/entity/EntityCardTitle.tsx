import React from 'react';

import { Box, Typography } from '@mui/material';

import { InternalLink } from 'src/components';
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
      lineHeight="1.3"
      sx={{
        overflowWrap: 'anywhere',
        fontSize: compact ? '1em !important' : undefined,
        // Limit text to 3 lines and show ellipsis
        display: '-webkit-box',
        overflow: 'hidden',
        WebkitLineClamp: titleMaxLines,
        WebkitBoxOrient: 'vertical',
      }}
      variant={compact ? 'body1' : 'h5'}
      title={title}
      {...rest}
    >
      {title}
    </Typography>
  );

  return (
    <Box display="flex" flexWrap="wrap">
      {withLink ? (
        <InternalLink to={`${baseUrl}/entities/${uid}`} underline="none">
          {titleNode}
        </InternalLink>
      ) : (
        titleNode
      )}
    </Box>
  );
};

export default EntityCardTitle;
