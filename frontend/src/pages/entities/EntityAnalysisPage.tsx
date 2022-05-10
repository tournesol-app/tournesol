import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';

import { Box, Button, Container, Grid, Typography } from '@mui/material';

import { LoaderWrapper } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { VideoAnalysis } from 'src/pages/videos/VideoAnalysisPage';
import { ApiError, PollsService, Recommendation } from 'src/services/openapi';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';

import { videoWithScoresFromRecommendation } from 'src/utils/entity';

const CandidateAnalysisPage = React.lazy(
  () => import('src/pages/entities/CandidateAnalysisPage')
);

const EntityNotFound = ({ apiError }: { apiError: ApiError | undefined }) => {
  const { t } = useTranslation();

  const { options } = useCurrentPoll();
  const path = options?.path ?? '/';

  if (apiError == undefined) {
    return null;
  }

  let title: string;
  let message: string;

  switch (apiError.status) {
    case 404:
      title = t('entityNotFound.404.title');
      message = t('entityNotFound.404.message');
      break;
    default:
      title = t('entityNotFound.unexpected.title');
      message = t('entityNotFound.unexpected.message');
  }

  return (
    <Grid container justifyContent="center" textAlign="center">
      <Grid item xs={12}>
        <Typography variant="h2">{title}</Typography>
      </Grid>
      <Grid item xs={12}>
        <Typography variant="subtitle1">{message}</Typography>
      </Grid>
      <Grid item xs={12}>
        <Box mt={2}>
          <Button variant="contained" component={Link} to={path}>
            {t('pageNotFound.backToHomePage')}
          </Button>
        </Box>
      </Grid>
    </Grid>
  );
};

const EntityAnalysisPage = () => {
  const { uid } = useParams<{ uid: string }>();
  const { name: pollName } = useCurrentPoll();

  const [entity, setEntity] = useState<Recommendation>();
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState<ApiError>();

  useEffect(() => {
    async function getEntityWithPollStats(): Promise<Recommendation> {
      const entity = await PollsService.pollsEntitiesRetrieve({
        name: pollName,
        uid,
      });
      return entity;
    }

    getEntityWithPollStats()
      .then((entity) => {
        setEntity(entity);
        setIsLoading(false);
      })
      .catch((reason: ApiError) => {
        setApiError(reason);
        setIsLoading(false);
      });
  }, [pollName, uid]);

  return (
    <LoaderWrapper isLoading={isLoading}>
      {entity ? (
        <>
          {pollName === PRESIDENTIELLE_2022_POLL_NAME && (
            <CandidateAnalysisPage entity={entity} />
          )}
          {pollName === YOUTUBE_POLL_NAME && (
            <VideoAnalysis video={videoWithScoresFromRecommendation(entity)} />
          )}
        </>
      ) : (
        <Container>
          <Box py={2}>
            <EntityNotFound apiError={apiError} />
          </Box>
        </Container>
      )}
    </LoaderWrapper>
  );
};

export default EntityAnalysisPage;
