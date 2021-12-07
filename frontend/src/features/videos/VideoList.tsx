import React from 'react';

import { Typography, Box } from '@material-ui/core';
import VideoCard from '../videos/VideoCard';
import { CompareNowAction, AddToRateLaterList } from 'src/utils/action';
import { useLoginState } from 'src/hooks';
import { ActionList, VideoObject } from 'src/utils/types';

interface Props {
  videos: VideoObject[];
  settings?: ActionList;
  emptyMessage?: string;
}

const DEFAULT_MESSAGE = 'No video found.';

function VideoList({
  videos,
  settings = [],
  emptyMessage = DEFAULT_MESSAGE,
}: Props) {
  const { isLoggedIn } = useLoginState();

  const actions = isLoggedIn ? [CompareNowAction, AddToRateLaterList] : [];

  return (
    <>
      {videos.length ? (
        videos.map((video: VideoObject) => (
          <Box key={video.video_id} mx={1} my={2}>
            <VideoCard video={video} actions={actions} settings={settings} />
          </Box>
        ))
      ) : (
        <Typography variant="h5" component="h2">
          {emptyMessage}
        </Typography>
      )}
    </>
  );
}

export default VideoList;
