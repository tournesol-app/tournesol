import React from 'react';

import { Typography, Box } from '@material-ui/core';
import VideoCard from '../videos/VideoCard';
import { CompareNowAction, AddToRateLaterList } from 'src/utils/action';
import { useLoginState } from 'src/hooks';
import { ActionList, VideoObject } from 'src/utils/types';

interface Props {
  videos: VideoObject[];
  settings?: ActionList;
}

function VideoList({ videos, settings = [] }: Props) {
  const { isLoggedIn } = useLoginState();

  const actions = isLoggedIn ? [CompareNowAction, AddToRateLaterList] : [];

  return (
    <>
      {videos.length ? (
        videos.map((video: VideoObject) => (
          <Box key={video.video_id} margin={1}>
            <VideoCard video={video} actions={actions} settings={settings} />
          </Box>
        ))
      ) : (
        <Typography variant="h5" component="h2">
          No video corresponds to your search criterias
        </Typography>
      )}
    </>
  );
}

export default VideoList;
