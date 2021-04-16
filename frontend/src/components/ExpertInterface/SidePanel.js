import React, { useState } from 'react';

import { makeStyles } from '@material-ui/core/styles';

import VideoComments from '../VideoComments';
import VideoCard from '../VideoCard';
import { GET_VIDEO } from '../../api';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    flex: '1 1 auto',
    border: '1px solid black',
    overflowY: 'auto',
    overflowX: 'hiddent',
    padding: '4px',
  },
  videoCardContainer: {
    overflowX: 'auto',
  },
  commentContainer: {},
}));

export default ({ videoId }) => {
  const classes = useStyles();
  const [videoInfo, setVideoInfo] = useState(null);

  if (videoInfo === null) {
    setVideoInfo(false);
    GET_VIDEO(videoId, (x) => {
      setVideoInfo(x);
    });
  }

  return (
    <div className={classes.root}>
      <div className={classes.videoCardContainer}>
        {videoInfo ? (
          <VideoCard video={videoInfo} onlyInfo />
        ) : (
          'Loading info . . .'
        )}
      </div>
      <div className={classes.commentContainer}>
        <VideoComments videoId={videoId} />
      </div>
    </div>
  );
};
