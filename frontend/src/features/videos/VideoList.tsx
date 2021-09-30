import React from 'react';

import { Link } from 'react-router-dom';
import { Typography, Button, makeStyles, Grid } from '@material-ui/core';
import ListIcon from '@material-ui/icons/FormatListBulleted';
import type { PaginatedVideoList, Video } from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';

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
            <Grid item xs={12} sm={10}>
              <VideoCard video={video} actions={[]} />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                size="small"
                variant="contained"
                color="primary"
                startIcon={<ListIcon />}
              >
                <Link to={`/comparison/?videoA=${video.video_id}`}>
                  Compare this video
                </Link>
              </Button>
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
