import React from 'react';

import { Typography } from '@material-ui/core';
import type { PaginatedVideoList, Video } from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';

function VideoList({ videos }: { videos: PaginatedVideoList }) {
  return (
    <div>
      {videos.results?.length ? (
        videos.results.map((video: Video) => (
          <VideoCard video={video} key={video.video_id} />
        ))
      ) : (
        <Typography variant="h5" component="h2">
          No video corresponds to your research criterias
        </Typography>
      )}
    </div>
  );
}

export default VideoList;
