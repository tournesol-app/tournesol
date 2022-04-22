import React from 'react';
import { useParams } from 'react-router-dom';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

import Card from 'src/components/Card';
import VideoCard from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import CriteriaBarChart from 'src/components/CriteriaBarChart';
import { VideoPlayer } from 'src/components/entity/EntityImagery';

function VideoAnalysis() {
  const { video_id } = useParams<{ video_id: string }>();
  const video = useVideoMetadata(video_id);

  return (
    <Box display="flex" justifyContent="center">
      <Grid
        container
        spacing={2}
        justifyContent="center"
        maxWidth="md"
        sx={{ marginTop: 3, marginBottom: 3 }}
      >
        <Grid item xs={12} sx={{ aspectRatio: '16 / 9' }}>
          <VideoPlayer videoId={video_id} duration={video.duration} controls />
        </Grid>
        <Grid item xs={12}>
          <VideoCard video={video} showPlayer={false} />
        </Grid>
        <Grid item xs="auto">
          <Card>
            <CriteriaBarChart video={video} />
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default VideoAnalysis;
