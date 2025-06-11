import React from 'react';

import { Box, SxProps, Typography } from '@mui/material';

import { InternalLink } from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import { absolutePollBasePath } from 'src/utils/navigation';

const EntityCardTitle = ({
  uid,
  title,
  compact = true,
  titleMaxLines = 3,
  withLink = true,
  sx = {},
}: {
  uid: string;
  title: string;
  compact?: boolean;
  titleMaxLines?: number;
  withLink?: boolean;
  sx?: SxProps;
}) => {
  const { baseUrl } = useCurrentPoll();

  const titleNode = (
    <Typography
      variant={compact ? 'body1' : 'h5'}
      title={title}
      sx={[
        {
          color: 'text.primary',
          lineHeight: '1.3',
          overflowWrap: 'anywhere',
          // Limit text to 3 lines and show ellipsis
          display: '-webkit-box',
          overflow: 'hidden',
          WebkitLineClamp: titleMaxLines,
          WebkitBoxOrient: 'vertical',
        },
        ...(Array.isArray(sx) ? sx : [sx]),
        compact
          ? {
              fontSize: '1em !important',
            }
          : {
              fontSize: null,
            },
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
        <InternalLink
          to={`${absolutePollBasePath(baseUrl)}/entities/${uid}`}
          underline="none"
        >
          {titleNode}
        </InternalLink>
      ) : (
        titleNode
      )}
    </Box>
  );
};

export default EntityCardTitle;
