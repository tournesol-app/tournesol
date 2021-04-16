import React from 'react';

import { useParams } from 'react-router-dom';
import YouTube from 'react-youtube';

import ContentReport from './ContentReport';
import VideoReports from './VideoReports';

const opts = {
  height: '240',
  width: '420',
  playerVars: {
    // https://developers.google.com/youtube/player_parameters
    autoplay: 0,
  },
};

export default () => {
  const { videoId } = useParams();

  return (
    <>
      {window.ENABLE_YOUTUBE_VIDEO_EMBED === 1 ? (
        <YouTube videoId={videoId} opts={opts} />
      ) : <span>Youtube {videoId}</span>}

      <ContentReport videoId={videoId} />
      Existing reports:
      <VideoReports videoId={videoId} />
    </>
  );
};
