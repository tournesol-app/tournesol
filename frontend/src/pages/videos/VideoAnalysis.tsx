import React from 'react';
import { useParams } from 'react-router-dom';
import makeStyles from '@mui/styles/makeStyles';

import Card from 'src/components/Card';
import VideoCard from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import CriteriaRadarChart from 'src/components/CriteriaRadarChart';

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

function VideoAnalysis() {
  const classes = useStyles();
  const { video_id } = useParams<{ video_id: string }>();
  const video = useVideoMetadata(video_id);

  return (
    <div className={classes.root}>
      <VideoCard video={video} />
      <Card sx={{ marginTop: 3 }}>
        <CriteriaRadarChart video={video} />
      </Card>
    </div>
  );
}

export default VideoAnalysis;
