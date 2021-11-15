import React, { useState, useEffect } from 'react';

import { VideoSerializerWithCriteria as Video } from 'src/services/openapi/models/VideoSerializerWithCriteria';

import { getVideoInformation } from './VideoApi';

// FromVideoId is a wrapper component that allows to transform a component receiving
// as props `video: Video` to receive instead `videoId: string`
function FromVideoId(Component: any): any {
  function WrappedComponent({
    videoId,
    ...rest
  }: {
    videoId: string;
    rest: any;
  }) {
    const [video, setVideo] = useState({ video_id: '' } as Video);
    useEffect(() => {
      // Fetches the video metadata if they have not been fetched or `videoId` has changed
      const process = async () => setVideo(await getVideoInformation(videoId));
      if (video.video_id != videoId) process();
    }, [video, video.video_id, videoId]); // Only re-runs if `videoId` changes
    return <Component video={video} {...rest} />;
  }
  return WrappedComponent;
}

export default FromVideoId;
