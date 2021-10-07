import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import VideoCardFromId from '../../features/videos/VideoCardFromId';
import { useParams } from 'react-router-dom';

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
