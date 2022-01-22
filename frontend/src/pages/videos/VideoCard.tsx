import React from 'react';
import makeStyles from '@mui/styles/makeStyles';
import { useParams } from 'react-router-dom';
import { VideoCardFromId } from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import Container from '@mui/material/Container';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis } from 'recharts';
import CriteriaRadarChart from 'src/components/Radarchart_CriteriaScore';

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
  const video = useVideoMetadata(video_id);

  return (
    <div>
      <div className={classes.root}>
        <VideoCardFromId videoId={video_id} />
      </div>

      <Container maxWidth="sm">
        {CriteriaRadarChart({ video: video })}
      </Container>
    </div>
  );
}

export default VideoCardPage;
