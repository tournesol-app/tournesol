import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { useParams } from 'react-router-dom';
import VideoCard from 'src/features/videos/VideoCard';
import FromVideoId from 'src/features/videos/FromVideoId';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '420px',
    marginTop: 120,
  },
}));

const VideoCardFromId = FromVideoId(VideoCard);

function VideoCardPage() {
  const classes = useStyles();
  const { video_id } = useParams<{ video_id: string }>();

  return (
    <div>
      <div className={classes.root}>
        <VideoCardFromId videoId={video_id} actions={[]} />
      </div>
    </div>
  );
}

export default VideoCardPage;
