import React from 'react';
import { Navigate } from 'react-router-dom';
import { RedirectState } from 'src/features/login';
import { useLoginState } from 'src/hooks';
import { extractVideoId } from 'src/utils/video';

/*
  This component handles a shared content, received via the "share_target"
  defined in the PWA manifest.
*/
const SharedContent = () => {
  const { isLoggedIn } = useLoginState();
  const queryParams = new URLSearchParams(document.location.search);
  let sharedUrl = queryParams.get('url');
  if (!sharedUrl) {
    // The Youtube mobile app shares the video url as "text"
    sharedUrl = queryParams.get('text');
  }

  const videoId = extractVideoId(sharedUrl ?? '');
  if (!videoId) {
    return <Navigate to="/entities/invalid" replace />;
  }

  const destination = `/entities/yt:${videoId}`;
  const redirectState: RedirectState = { from: destination };
  if (!isLoggedIn) {
    return <Navigate to="/login" state={redirectState} replace />;
  }
  return <Navigate to={destination} replace />;
};

export default SharedContent;
