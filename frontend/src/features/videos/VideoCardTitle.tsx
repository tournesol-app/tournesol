import React from 'react';
import { Box, Typography } from '@mui/material';
import { VideoObject } from 'src/utils/types';

const VideoCardTitle = ({
  video,
  compact = true,
  titleMaxLines = 3,
  ...rest
}: {
  video: VideoObject;
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
        title={video.name}
        {...rest}
      >
        {video.name}
      </Typography>
    </Box>
  );
};

export default VideoCardTitle;
