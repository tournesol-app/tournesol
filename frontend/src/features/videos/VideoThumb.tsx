/* eslint-disable react/no-unescaped-entities */
import React from 'react';
import ReactPlayer from 'react-player/youtube';

import { makeStyles } from '@material-ui/core/styles';
import { Typography, Grid } from '@material-ui/core';

import type { VideoSerializerWithCriteria } from 'src/services/openapi';
import { ActionList } from 'src/utils/types';

const useStyles = makeStyles(() => ({
  main: {
    margin: 4,
    maxWidth: 1000,
    width: 'calc(100% - 10px)',
    background: '#FFFFFF',
    border: '1px solid #DCD8CB',
    boxShadow:
      '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  title: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    color: '#1D1A14',
  },
  youtube_complements: {
    margin: 4,
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 'normal',
    fontSize: '13px',
    lineHeight: '19px',
    color: '#B6B1A1',
  },
  youtube_complements_p: {
    marginRight: '12px',
  },
  channel: {
    textDecorationLine: 'underline',
  },
  actionsContainer: {
    display: 'flex',
    alignItems: 'end',
    flexDirection: 'row',
  },
}));

// VideoThumb is similar to the VideoCard component but displays a lot less information
function VideoThumb({
  video,
  actions = [],
}: {
  video: VideoSerializerWithCriteria;
  actions: ActionList;
}) {
  const classes = useStyles();
  const videoId = video.video_id;

  return (
    <Grid container spacing={1} className={classes.main}>
      <Grid item xs={12} style={{ aspectRatio: '16 / 9', padding: 0 }}>
        <ReactPlayer
          url={`https://youtube.com/watch?v=${videoId}`}
          light
          width="100%"
          height="100%"
        />
      </Grid>
      <Grid item xs={12}>
        <Typography className={classes.title}>{video.name}</Typography>
        <div className={classes.youtube_complements}>
          {video.views && (
            <span className={classes.youtube_complements_p}>
              {video.views} views
            </span>
          )}
          {video.publication_date && (
            <span className={classes.youtube_complements_p}>
              {video.publication_date}
            </span>
          )}
          {video.uploader && (
            <span className={classes.channel}>{video.uploader}</span>
          )}
        </div>
      </Grid>
      <Grid item xs={12} className={classes.actionsContainer}>
        {actions.map((Action, index) => (
          <Action key={index} videoId={videoId} />
        ))}
      </Grid>
    </Grid>
  );
}

export default VideoThumb;
