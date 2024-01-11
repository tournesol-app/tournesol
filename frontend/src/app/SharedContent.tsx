import React from 'react';
import { Redirect } from 'react-router-dom';
import RedirectState from 'src/features/login/RedirectState';
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
    return <Redirect to="/entities/invalid" />;
  }

  const destination = `/entities/yt:${videoId}`;
  if (!isLoggedIn) {
    return (
      <Redirect
        to={{
          pathname: '/login',
          state: { from: destination } as RedirectState,
        }}
      />
    );
  }
  return <Redirect to={destination} />;
};

export default SharedContent;
