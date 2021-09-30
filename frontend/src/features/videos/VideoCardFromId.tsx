import React, { useState, useEffect } from 'react';

import type { Video } from 'src/services/openapi';

import VideoCard from './VideoCard';
import { getVideoInformation } from './VideoApi';

function VideoCardFromId({ videoId }: { videoId: string }) {
  const [video, setVideo] = useState({ video_id: '' });

  useEffect(() => {
    // Fetches the video metadata if they have not been fetched or `videoId` has changed
    if (video.video_id != videoId) {
      getVideoInformation(videoId, (video: Video) => {
        setVideo(video);
      });
    }
  }, [video, video.video_id, videoId]); // Only re-runs if `videoId` changes
  return <VideoCard video={video} actions={[]} />;
}

export default VideoCardFromId;
