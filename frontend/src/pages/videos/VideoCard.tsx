import React from 'react';
import RadarChart from 'react-svg-radar-chart';
import 'react-svg-radar-chart/build/css/index.css';
import makeStyles from '@mui/styles/makeStyles';
import { useParams } from 'react-router-dom';
import { VideoCardFromId } from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import Container from '@mui/material/Container';

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
  console.log(video_id);
  const video = useVideoMetadata(video_id);
  console.log(video);
  const captions: any = video.criteria_scores
    ? video.criteria_scores.length > 0
      ? Object.fromEntries(
          video.criteria_scores.map((criteria) => [
            criteria.criteria,
            criteria.criteria,
          ])
        )
      : {
          d: 'd',
        }
    : null;

  const data: any = video.criteria_scores
    ? video.criteria_scores.length > 0
      ? {
          data: Object.fromEntries(
            video.criteria_scores.map((criteria) => [
              criteria.criteria,
              criteria.score,
            ])
          ),
          meta: { color: 'purple' },
        }
      : {
          data: {
            d: 0,
          },
          meta: { color: 'blue' },
        }
    : null;
  console.log(captions);
  console.log(video.criteria_scores);
  return (
    <div>
      <div className={classes.root}>
        <VideoCardFromId videoId={video_id} />
      </div>
      <Container maxWidth="sm">
        {video.criteria_scores && (
          <RadarChart captions={captions} data={[data]} size={550} />
        )}
      </Container>
    </div>
  );
}

export default VideoCardPage;
