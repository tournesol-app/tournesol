import React from 'react';

import { Typography, makeStyles, Grid } from '@material-ui/core';
import type { PaginatedVideoList, Video } from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';
import { CompareNowAction } from 'src/utils/action';

const useStyles = makeStyles(() => ({
  card: {
    alignItems: 'center',
  },
}));

function VideoList({ videos }: { videos: PaginatedVideoList }) {
  const classes = useStyles();

  return (
    <div>
      {videos.results?.length ? (
        videos.results.map((video: Video) => (
          <Grid container className={classes.card} key={video.video_id}>
            <Grid item xs={12}>
              <VideoCard video={video} actions={[CompareNowAction]} />
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
