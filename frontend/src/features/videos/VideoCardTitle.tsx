import React from 'react';
import { Box, Typography } from '@mui/material';
import { VideoObject } from 'src/utils/types';

const VideoCardTitle = ({
  video,
  titleMaxLines = 3,
  ...rest
}: {
  video: VideoObject;
  titleMaxLines?: number;
  [propName: string]: unknown;
}) => {
  return (
    <Box display="flex" flexWrap="wrap">
      <Typography
        sx={{
          // Limit text to 3 lines and show ellipsis
          display: '-webkit-box',
          overflow: 'hidden',
          WebkitLineClamp: titleMaxLines,
          WebkitBoxOrient: 'vertical',
        }}
        title={video.name}
        fontSize="1.1em"
        {...rest}
      >
        {video.name}
      </Typography>
    </Box>
  );
};

export default VideoCardTitle;
