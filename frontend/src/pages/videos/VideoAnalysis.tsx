import React from 'react';
import { useParams } from 'react-router-dom';
import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';

import Card from 'src/components/Card';
import VideoCardAnalysis from 'src/features/videos/VideoCardAnalysis';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
{/*import CriteriaRadarChart from 'src/components/CriteriaRadarChart';*/}
import CriteriaBarChart from 'src/components/CriteriaBarChart';

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
     {/* <VideoCard video={video} widthVideo={960} />*/}
     <VideoCardAnalysis video={video} />
      <Grid
        container
        spacing={2}
        justifyContent="center"
        sx={{ marginTop: 3, marginBottom: 3 }}
      >
        <Grid item xs="auto">
          {/* <Card>
            <CriteriaRadarChart video={video} />
          </Card> */}
        </Grid>
        <Grid item xs="auto">
          <Card>
            <CriteriaBarChart video={video} />
          </Card>
        </Grid>
      </Grid>
    </div>
  );
}

export default VideoAnalysis;
