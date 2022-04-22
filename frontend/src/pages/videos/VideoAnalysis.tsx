import React from 'react';
import { useParams } from 'react-router-dom';
import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';

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
<<<<<<< HEAD
      <VideoCard video={video} />
      <Box
        sx={{
          marginTop: 3,
          marginBottom: 3,
          width: '100%',
          maxWidth: 1000,
        }}
      >
        <Grid container spacing={2} justifyContent="center">
          <Grid item xs={12} md={6}>
            <Card>
              <CriteriaRadarChart video={video} />
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CriteriaBarChart video={video} />
            </Card>
          </Grid>
=======
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
>>>>>>> d8ac3bab ([draft] front: Remove radar chart and bigger VideoPlayer on VideoAnalysis (#829))
        </Grid>
      </Box>
    </div>
  );
}

export default VideoAnalysis;
