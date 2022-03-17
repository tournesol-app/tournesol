import React from 'react';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import HomeVideoPage from 'src/pages/home/videos/HomeVideos';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';

const HomePage = () => {
  const { name: pollName } = useCurrentPoll();

  if (pollName === YOUTUBE_POLL_NAME) {
    return <HomeVideoPage />;
  }

  if (pollName === PRESIDENTIELLE_2022_POLL_NAME) {
    return <></>;
  }

  return <></>;
};

export default HomePage;
