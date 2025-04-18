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
      variant={compact ? 'body1' : 'h5'}
      title={title}
      {...rest}
      sx={[
        {
          color: 'text.primary',
          lineHeight: '1.3',
          overflowWrap: 'anywhere',
          fontSize: compact ? '1em !important' : undefined,

          // Limit text to 3 lines and show ellipsis
          display: '-webkit-box',

          overflow: 'hidden',
          WebkitLineClamp: titleMaxLines,
          WebkitBoxOrient: 'vertical',
        },
        ...(Array.isArray(rest.sx) ? rest.sx : [rest.sx]),
      ]}
    >
      {title}
    </Typography>
  );

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
      }}
    >
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
