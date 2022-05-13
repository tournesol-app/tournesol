import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

import { Box, Grid, Paper, Typography } from '@mui/material';

import CriteriaBarChart from 'src/components/CriteriaBarChart';
import { VideoPlayer } from 'src/components/entity/EntityImagery';
import CriteriaScoresDistribution from 'src/features/charts/CriteriaScoresDistribution';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import VideoCard from 'src/features/videos/VideoCard';
import { useLoginState } from 'src/hooks';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { PersonalCriteriaScoresContextProvider } from 'src/hooks/usePersonalCriteriaScores';
import PersonalScoreCheckbox from 'src/components/PersonalScoreCheckbox';
import { CompareNowAction, AddToRateLaterList } from 'src/utils/action';

export const VideoAnalysis = ({
  video,
}: {
  video: VideoSerializerWithCriteria;
}) => {
  const { t } = useTranslation();
  const { uid } = video;
  const actions = useLoginState() ? [CompareNowAction, AddToRateLaterList] : [];

  const { criteria_scores: criteriaScores } = video;
  const shouldDisplayCharts = criteriaScores && criteriaScores.length > 0;

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
          <VideoCard video={video} actions={actions} showPlayer={false} />
        </Grid>

        {/* data visualization */}
        {shouldDisplayCharts && (
          <>
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
                <PersonalCriteriaScoresContextProvider uid={uid}>
                  <Box px={2} pt={1}>
                    <PersonalScoreCheckbox />
                  </Box>
                  <Box p={1}>
                    <CriteriaBarChart video={video} />
                  </Box>
                </PersonalCriteriaScoresContextProvider>
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
                  <CriteriaScoresDistribution uid={uid} />
                </Box>
              </Paper>
            </Grid>
          </>
        )}
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
