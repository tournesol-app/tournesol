import React from 'react';
import RadarChart from 'react-svg-radar-chart';
import 'react-svg-radar-chart/build/css/index.css';
import makeStyles from '@mui/styles/makeStyles';
import { useParams } from 'react-router-dom';
import { VideoCardFromId } from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';

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

  const captions: any = video.criteria_scores
    ? Object.fromEntries(
        video.criteria_scores.map((criteria) => [
          criteria.criteria,
          criteria.criteria,
        ])
      )
    : null;

  const data: any = video.criteria_scores
    ? {
        data: Object.fromEntries(
          video.criteria_scores.map((criteria) => [
            criteria.criteria,
            criteria.score,
          ])
        ),
        meta: { color: 'blue' },
      }
    : null;
  return (
    <div>
      <div className={classes.root}>
        <VideoCardFromId videoId={video_id} />
      </div>
      <div>
        {video.criteria_scores && (
          <RadarChart captions={captions} data={[data]} size={550} />
        )}
      </div>
    </div>
  );
}

export default VideoCardPage;
