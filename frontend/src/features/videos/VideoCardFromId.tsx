import React, { useState, useEffect } from 'react';

import { VideoSerializerWithCriteria as Video } from 'src/services/openapi/models/VideoSerializerWithCriteria';

import VideoCard from './VideoCard';
import { getVideoInformation } from './VideoApi';
import { ActionList } from 'src/utils/types';

function VideoCardFromId({
  videoId,
  actions,
}: {
  videoId: string;
  actions: ActionList;
}) {
  const [video, setVideo] = useState({ video_id: '' } as Video);

  useEffect(() => {
    // Fetches the video metadata if they have not been fetched or `videoId` has changed
    if (video.video_id != videoId) {
      getVideoInformation(videoId, (video: Video) => {
        setVideo(video);
      });
    }
  }, [video, video.video_id, videoId]); // Only re-runs if `videoId` changes
  return <VideoCard video={video} actions={actions} />;
}

export default VideoCardFromId;
