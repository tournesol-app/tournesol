import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Grid, Paper, Typography } from '@mui/material';

import VideoCard from 'src/features/videos/VideoCard';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import CriteriaBarChart from 'src/components/CriteriaBarChart';
import { VideoPlayer } from 'src/components/entity/EntityImagery';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { useTranslation } from 'react-i18next';
import CriteriaScoresDistribution from 'src/features/charts/CriteriaScoresDistribution';

export const VideoAnalysis = ({
  video,
}: {
  video: VideoSerializerWithCriteria;
}) => {
  const { t } = useTranslation();
  const entityId = `yt:${video.video_id}`;
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
          <VideoPlayer
            videoId={video.video_id}
            duration={video.duration}
            controls
          />
        </Grid>
        <Grid item xs={12}>
          <VideoCard video={video} showPlayer={false} />
        </Grid>

        {/* data visualization */}
        <Grid item xs={12} sm={12} md={6}>
          <Paper>
            <Box
              p={1}
              bgcolor="rgb(238, 238, 238)"
              display="flex"
              justifyContent="center"
            >
              <Typography variant="h5">
                {t('entityAnalysisPage.chart.criteriaScores.title')}
              </Typography>
            </Box>
            <Box p={1}>
              <CriteriaBarChart video={video} />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={12} md={6}>
          <Paper>
            <Box
              p={1}
              bgcolor="rgb(238, 238, 238)"
              display="flex"
              justifyContent="center"
            >
              <Typography variant="h5">
                {t('criteriaScoresDistribution.title')}
              </Typography>
            </Box>
            <Box p={1}>
              <CriteriaScoresDistribution uid={entityId} />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

const VideoAnalysisPage = () => {
  const { video_id } = useParams<{ video_id: string }>();
  const video = useVideoMetadata(video_id);

  return <VideoAnalysis video={video} />;
};

export default VideoAnalysisPage;
