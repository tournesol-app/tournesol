import React from 'react';
import { useParams } from 'react-router-dom';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import { VideoAnalysis } from 'src/pages/videos/VideoAnalysisPage';

const CandidateAnalysisPage = React.lazy(
  () => import('src/pages/entities/CandidateAnalysisPage')
);

const EntityAnalysisPage = () => {
  const { uid } = useParams<{ uid: string }>();
  const { name: pollName } = useCurrentPoll();
  // TODO refator this to use the new endpoint for all entities
  const video = useVideoMetadata(uid.split(':')[1]);

  if (pollName === YOUTUBE_POLL_NAME) {
    return <VideoAnalysis video={video} />;
  }
  if (pollName === PRESIDENTIELLE_2022_POLL_NAME) {
    return <CandidateAnalysisPage />;
  }
  return null;
};

export default EntityAnalysisPage;
