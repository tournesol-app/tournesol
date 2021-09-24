import React from 'react';

import { Link } from 'react-router-dom';
import { Typography, Button, makeStyles } from '@material-ui/core';
import type { PaginatedVideoList, Video } from 'src/services/openapi';
import VideoCard from '../videos/VideoCard';

const useStyles = makeStyles(() => ({
  card: {
    display: 'flex',
    alignItems: 'center',
    textAlign: 'center',
  },
}));

function VideoList({ videos }: { videos: PaginatedVideoList }) {
  const classes = useStyles();

  return (
    <div>
      {videos.results?.length ? (
        videos.results.map((video: Video) => (
          <div className={classes.card} key={video.video_id}>
            <VideoCard video={video} />
            <Button size="small" variant="contained" color="primary">
              <Link to={`/comparison/?videoA=${video.video_id}`}>
                Compare this video
              </Link>
            </Button>
          </div>
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
