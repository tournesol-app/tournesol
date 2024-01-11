import React from 'react';
import { Redirect } from 'react-router-dom';
import { extractVideoId } from 'src/utils/video';

/*
  This component handles a shared content, received via the "share_target"
  defined in the PWA manifest.
*/
const SharedContent = () => {
  const queryParams = new URLSearchParams(document.location.search);
  const sharedUrl = queryParams.get('url');
  const videoId = extractVideoId(sharedUrl ?? '');
  if (!videoId) {
    return <Redirect to="/" />;
  }
  return <Redirect to={`/comparison/?uidA=yt:${videoId}`} />;
};

export default SharedContent;
