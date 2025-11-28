import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigate, useParams } from 'react-router-dom';

import { Box, Collapse, Grid2, Paper, Typography } from '@mui/material';

import CollapseButton from 'src/components/CollapseButton';
import CriteriaBarChart from 'src/components/CriteriaBarChart';
import { YoutubeVideoPlayer } from 'src/components/entity/EntityImagery';
import CriteriaScoresDistribution from 'src/features/charts/CriteriaScoresDistribution';
import EntityContextBox from 'src/features/entity_context/EntityContextBox';
import ContextualRecommendations from 'src/features/recommendation/ContextualRecommendations';
import EntityCard from 'src/components/entity/EntityCard';
import { useLoginState, useScrollToLocation } from 'src/hooks';
import { ContributorRating, Recommendation } from 'src/services/openapi';
import { SelectedCriterionProvider } from 'src/hooks/useSelectedCriterion';
import PersonalScoreCheckbox from 'src/components/PersonalScoreCheckbox';
import { CompareNowAction, AddToRateLaterList } from 'src/utils/action';
import linkifyStr from 'linkify-string';
import VideoAnalysisActionBar from './VideoAnalysisActionBar';
import useContributorRating from 'src/hooks/useContributorRating';

export const VideoAnalysis = ({
  entityResult,
}: {
  entityResult: Recommendation | ContributorRating;
}) => {
  const { t } = useTranslation();
  const [descriptionCollapsed, setDescriptionCollapsed] = useState(false);
  const actions = useLoginState() ? [CompareNowAction, AddToRateLaterList] : [];
  useScrollToLocation();

  const { contributorRating, loadContributorRating } = useContributorRating();
  const video = contributorRating ?? entityResult;

  const entity = video.entity;
  const criteriaScores = video.collective_rating?.criteria_scores ?? [];
  const shouldDisplayCharts = criteriaScores.length > 0;

  const linkifyOpts = { defaultProtocol: 'https', target: '_blank' };
  const linkifiedDescription = linkifyStr(
    entity.metadata.description || '',
    linkifyOpts
  );

  return (
    <Box
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: '16px',
        justifyContent: 'space-between',
      }}
    >
      <Box
        sx={{
          flex: 2,
          minWidth: { xs: '100%', md: null },
        }}
      >
        {/* Entity section, with its player, title, scores and actions. */}
        <Grid2
          container
          spacing={2}
          sx={{
            justifyContent: 'center',
          }}
        >
          <Grid2 sx={{ aspectRatio: '16 / 9' }} size={12}>
            <YoutubeVideoPlayer
              videoId={entity.metadata.video_id}
              duration={entity.metadata.duration}
              controls
            />
          </Grid2>
          <Grid2 size={12}>
            <VideoAnalysisActionBar
              video={video}
              onContributorRatingUpdateSuccessCb={loadContributorRating}
            />
          </Grid2>
          <Grid2 size={12}>
            <EntityCard
              result={video}
              actions={actions}
              displayImage={false}
              showEntitySeenIndicator={true}
            />
          </Grid2>
          {video.entity_contexts.length > 0 && (
            <Grid2 size={12}>
              <EntityContextBox
                uid={video.entity.uid}
                contexts={video.entity_contexts}
              />
            </Grid2>
          )}
          <Grid2 size={12}>
            <CollapseButton
              expanded={descriptionCollapsed}
              onClick={() => {
                setDescriptionCollapsed(!descriptionCollapsed);
              }}
            >
              {t('entityAnalysisPage.video.description')}
            </CollapseButton>
            <Collapse in={descriptionCollapsed} timeout="auto" unmountOnExit>
              <Typography
                component="div"
                sx={{
                  my: 2,
                }}
              >
                <Box
                  style={
                    descriptionCollapsed
                      ? { display: 'block' }
                      : { display: 'none' }
                  }
                  dangerouslySetInnerHTML={{ __html: linkifiedDescription }}
                  sx={{
                    fontSize: '0.9em',
                    whiteSpace: 'pre-wrap',
                  }}
                />
              </Typography>
            </Collapse>
          </Grid2>

          {/* Data visualization. */}
          {shouldDisplayCharts && (
            <SelectedCriterionProvider>
              <Grid2
                size={{
                  xs: 12,
                  sm: 12,
                  md: 6,
                }}
              >
                <Paper>
                  <Box
                    sx={{
                      p: 1,
                      bgcolor: 'rgb(238, 238, 238)',
                      display: 'flex',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h5">
                      {t('entityAnalysisPage.chart.criteriaScores.title')}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      px: 2,
                      pt: 1,
                    }}
                  >
                    <PersonalScoreCheckbox />
                  </Box>
                  <Box
                    sx={{
                      p: 1,
                    }}
                  >
                    <CriteriaBarChart entityResult={video} />
                  </Box>
                </Paper>
              </Grid2>
              <Grid2
                size={{
                  xs: 12,
                  sm: 12,
                  md: 6,
                }}
              >
                <Paper sx={{ height: '100%' }}>
                  <Box
                    sx={{
                      p: 1,
                      bgcolor: 'rgb(238, 238, 238)',
                      display: 'flex',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h5">
                      {t('criteriaScoresDistribution.title')}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      p: 1,
                    }}
                  >
                    <CriteriaScoresDistribution entityResult={video} />
                  </Box>
                </Paper>
              </Grid2>
            </SelectedCriterionProvider>
          )}
        </Grid2>
      </Box>
      <Box
        sx={{
          flex: 1,
        }}
      >
        <ContextualRecommendations
          contextUid={entity.uid}
          uploader={entity.metadata.uploader || undefined}
        />
      </Box>
    </Box>
  );
};

const VideoAnalysisPage = () => {
  const { video_id } = useParams<{ video_id: string }>();
  return <Navigate to={`/entities/yt:${video_id}`} replace />;
};

export default VideoAnalysisPage;
