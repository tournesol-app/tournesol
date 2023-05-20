import React from 'react';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import HomeVideoPage from 'src/pages/home/videos/HomeVideos';
import HomePresidentielle2022Page from 'src/pages/home/presidentielle2022/HomePresidentielle2022';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { useScrollToLocation } from 'src/hooks';

const HomePage = () => {
  const { name: pollName } = useCurrentPoll();
  useScrollToLocation();

  if (pollName === YOUTUBE_POLL_NAME) {
    return <HomeVideoPage />;
  }

  if (pollName === PRESIDENTIELLE_2022_POLL_NAME) {
    return <HomePresidentielle2022Page />;
  }

  return <></>;
};

export default HomePage;
