import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';

import { Box, Button, Container, Grid, Typography } from '@mui/material';

import { LoaderWrapper } from 'src/components';
import { useCurrentPoll, useLoginState } from 'src/hooks';
import {
  ApiError,
  PollsService,
  Recommendation,
  VideoService,
} from 'src/services/openapi';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { extractVideoId } from 'src/utils/video';

const CandidateAnalysisPage = React.lazy(
  () => import('src/pages/entities/CandidateAnalysisPage')
);

const VideoAnalysis = React.lazy(() =>
  import('src/pages/videos/VideoAnalysisPage').then(({ VideoAnalysis }) => ({
    default: VideoAnalysis,
  }))
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
  const { isLoggedIn } = useLoginState();

  const { i18n } = useTranslation();
  const currentLang = i18n.resolvedLanguage;

  const [entity, setEntity] = useState<Recommendation>();
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState<ApiError>();

  const tryToCreateVideo = async () => {
    if (pollName !== YOUTUBE_POLL_NAME) {
      return false;
    }
    if (!isLoggedIn) {
      return false;
    }
    const videoId = extractVideoId(uid);
    if (!videoId) {
      return false;
    }
    try {
      await VideoService.videoCreate({
        requestBody: {
          video_id: videoId,
        },
      });
      return true;
    } catch (err) {
      console.error(err);
      return false;
    }
  };

  useEffect(() => {
    setIsLoading(true);

    async function getEntityWithPollStats(): Promise<Recommendation> {
      const entity = await PollsService.pollsEntitiesRetrieve({
        name: pollName,
        uid,
      });
      return entity;
    }

    async function getEntity(createVideo = true): Promise<void> {
      try {
        const entity = await getEntityWithPollStats();
        setEntity(entity);
      } catch (error) {
        const reason: ApiError = error;
        if (reason.status === 404 && createVideo) {
          const created = await tryToCreateVideo();
          if (created) {
            return getEntity(false);
          }
        }
        setApiError(reason);
      }
    }

    getEntity().finally(() => {
      setIsLoading(false);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentLang, pollName, uid]);

  return (
    <LoaderWrapper isLoading={isLoading}>
      {entity ? (
        <>
          {pollName === PRESIDENTIELLE_2022_POLL_NAME && (
            <CandidateAnalysisPage entity={entity} />
          )}
          {pollName === YOUTUBE_POLL_NAME && <VideoAnalysis video={entity} />}
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
