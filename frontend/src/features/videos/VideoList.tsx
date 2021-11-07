import React from 'react';

import { Typography, makeStyles, Grid } from '@material-ui/core';
import type {
  PaginatedVideoSerializerWithCriteriaList,
  VideoSerializerWithCriteria,
} from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';
import { CompareNowAction, AddToRateLaterList } from 'src/utils/action';
import { useLoginState } from 'src/hooks';

const useStyles = makeStyles(() => ({
  card: {
    alignItems: 'center',
  },
}));

function VideoList({
  videos,
}: {
  videos: PaginatedVideoSerializerWithCriteriaList;
}) {
  const classes = useStyles();
  const { isLoggedIn } = useLoginState();

  const actions = isLoggedIn ? [CompareNowAction, AddToRateLaterList] : [];

  return (
    <div>
      {videos.results?.length ? (
        videos.results.map((video: VideoSerializerWithCriteria) => (
          <Grid container className={classes.card} key={video.video_id}>
            <Grid item xs={12}>
              <VideoCard video={video} actions={actions} />
            </Grid>
          </Grid>
        ))
      ) : (
        <Typography variant="h5" component="h2">
          No video corresponds to your research criterias
        </Typography>
      )}
    </div>
  );
}

export default VideoList;
