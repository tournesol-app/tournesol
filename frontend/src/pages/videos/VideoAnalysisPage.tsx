import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, Link as RouterLink } from 'react-router-dom';

import { Box, Button, Collapse, Grid, Paper, Typography } from '@mui/material';
import { Compare } from '@mui/icons-material';

import CopyToClipboardButton from 'src/components/buttons/CopyToClipboardButton';
import CollapseButton from 'src/components/CollapseButton';
import CriteriaBarChart from 'src/components/CriteriaBarChart';
import { VideoPlayer } from 'src/components/entity/EntityImagery';
import CriteriaScoresDistribution from 'src/features/charts/CriteriaScoresDistribution';
import { useVideoMetadata } from 'src/features/videos/VideoApi';
import VideoCard from 'src/features/videos/VideoCard';
import { useCurrentPoll, useLoginState } from 'src/hooks';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { PersonalCriteriaScoresContextProvider } from 'src/hooks/usePersonalCriteriaScores';
import PersonalScoreCheckbox from 'src/components/PersonalScoreCheckbox';
import { CompareNowAction, AddToRateLaterList } from 'src/utils/action';
import linkifyStr from 'linkify-string';
import { SelectedCriterionProvider } from 'src/hooks/useSelectedCriterion';
import ContextualRecommendations from 'src/features/recommendation/ContextualRecommendations';

export const VideoAnalysis = ({
  video,
}: {
  video: VideoSerializerWithCriteria;
}) => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();
  const [descriptionCollapsed, setDescriptionCollapsed] = React.useState(false);

  const uid = `yt:${video.video_id}`;
  const actions = useLoginState() ? [CompareNowAction, AddToRateLaterList] : [];

  const { criteria_scores: criteriaScores } = video;
  const shouldDisplayCharts = criteriaScores && criteriaScores.length > 0;

  const linkifyOpts = { defaultProtocol: 'https', target: '_blank' };
  const linkifiedDescription = linkifyStr(video.description || '', linkifyOpts);

  return (
    <Box
      p={2}
      display="flex"
      flexDirection="row"
      flexWrap="wrap"
      gap="16px"
      justifyContent="space-between"
    >
      <Box flex={2} minWidth={{ xs: '100%', md: null }}>
        {/* Top level section, containing links and maybe more in the future. */}
        <Box mb={2} display="flex" justifyContent="flex-end" gap="8px">
          <CopyToClipboardButton />
          <Button
            color="secondary"
            variant="contained"
            endIcon={<Compare />}
            component={RouterLink}
            to={`${baseUrl}/comparison?uidA=${uid}`}
          >
            {t('entityAnalysisPage.generic.compare')}
          </Button>
        </Box>

        {/* Entity section, with its player, title, scores and actions. */}
        <Grid container spacing={2} justifyContent="center">
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
          <Grid item xs={12}>
            <CollapseButton
              expanded={descriptionCollapsed}
              onClick={() => {
                setDescriptionCollapsed(!descriptionCollapsed);
              }}
            >
              {t('entityAnalysisPage.video.description')}
            </CollapseButton>
            <Collapse in={descriptionCollapsed} timeout="auto" unmountOnExit>
              <Typography paragraph>
                <Box
                  style={
                    descriptionCollapsed
                      ? { display: 'block' }
                      : { display: 'none' }
                  }
                  dangerouslySetInnerHTML={{ __html: linkifiedDescription }}
                  fontSize="0.9em"
                  whiteSpace="pre-wrap"
                />
              </Typography>
            </Collapse>
          </Grid>

          {/* Data visualization. */}
          {shouldDisplayCharts && (
            <SelectedCriterionProvider>
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
            </SelectedCriterionProvider>
          )}
        </Grid>
      </Box>
      <Box flex={1}>
        <ContextualRecommendations
          contextUid={uid}
          uploader={video.uploader || undefined}
        />
      </Box>
    </Box>
  );
};

const VideoAnalysisPage = () => {
  const { video_id } = useParams<{ video_id: string }>();
  const video = useVideoMetadata(video_id);

  return <VideoAnalysis video={video} />;
};

export default VideoAnalysisPage;
