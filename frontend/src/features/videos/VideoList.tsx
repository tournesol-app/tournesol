import React from 'react';

import { Typography, Box } from '@mui/material';
import VideoCard from '../videos/VideoCard';
import {
  CompareNowAction,
  AddToRateLaterList,
  AnalysisPageLink,
} from 'src/utils/action';
import { useLoginState } from 'src/hooks';
import { ActionList, VideoObject } from 'src/utils/types';

interface Props {
  videos: VideoObject[];
  actions?: ActionList;
  settings?: ActionList;
  emptyMessage?: React.ReactNode;
  personalScores?: { [uid: string]: number };
}

const DEFAULT_MESSAGE = 'No video found.';

/**
 * THIS COMPONENT IS DEPRECATED. USE `EntityList` INSTEAD.
 *
 * This component is only used by the rate-later page, which is connected
 * to a legacy API endpoint returning VideoObject instead of new style entity.
 *
 * TODO:
 *  - make the rate-later component return entities
 *  - use the `EntityList` in the rate-later page
 *  - delete this component
 */
function VideoList({
  videos,
  actions,
  settings = [],
  emptyMessage = DEFAULT_MESSAGE,
  personalScores,
}: Props) {
  const { isLoggedIn } = useLoginState();

  const defaultActions = isLoggedIn
    ? [CompareNowAction, AddToRateLaterList, AnalysisPageLink]
    : [AnalysisPageLink];

  return (
    <>
      {videos.length ? (
        videos.map((video: VideoObject) => (
          <Box key={video.uid} mx={1} my={2}>
            <VideoCard
              video={video}
              actions={actions ?? defaultActions}
              settings={settings}
              personalScore={
                personalScores ? personalScores[video.uid] : undefined
              }
            />
          </Box>
        ))
      ) : (
        <Box m={2}>
          <Typography variant="h5" component="h2" align="center">
            {emptyMessage}
          </Typography>
        </Box>
      )}
    </>
  );
}

export default VideoList;
