import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { TFunction } from 'i18next';

import { Box, Button, Container, Grid2, Typography } from '@mui/material';

import { LoaderWrapper } from 'src/components';
import { useCurrentPoll, useLoginState, useDocumentTitle } from 'src/hooks';
import {
  ApiError,
  PollsService,
  Recommendation,
  RelatedEntity,
  VideoService,
} from 'src/services/openapi';
import {
  DEFAULT_DOCUMENT_TITLE,
  getEntityMetadataName,
  getPollName,
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { extractVideoId } from 'src/utils/video';
import { ContributorRatingContextProvider } from 'src/hooks/useContributorRating';

const CandidateAnalysisPage = React.lazy(
  () => import('src/pages/entities/CandidateAnalysisPage')
);

const VideoAnalysis = React.lazy(() =>
  import('src/pages/videos/VideoAnalysisPage').then(({ VideoAnalysis }) => ({
    default: VideoAnalysis,
  }))
);

const createPageTitle = (
  t: TFunction,
  pollName: string,
  entity: RelatedEntity
): string | undefined => {
  const entityName = getEntityMetadataName(pollName, entity);
  if (!entityName) {
    return undefined;
  }

  switch (pollName) {
    case YOUTUBE_POLL_NAME:
      return `${entityName} | Tournesol ${getPollName(t, pollName)}`;
    default:
      return undefined;
  }
};

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
    <Grid2
      container
      sx={{
        justifyContent: 'center',
        textAlign: 'center',
      }}
    >
      <Grid2 size={12}>
        <Typography variant="h2">{title}</Typography>
      </Grid2>
      <Grid2 size={12}>
        <Typography variant="subtitle1">{message}</Typography>
      </Grid2>
      <Grid2 size={12}>
        <Box
          sx={{
            mt: 2,
          }}
        >
          <Button variant="contained" component={Link} to={path}>
            {t('pageNotFound.backToHomePage')}
          </Button>
        </Box>
      </Grid2>
    </Grid2>
  );
};

const EntityAnalysisPage = () => {
  const { uid } = useParams<{ uid: string }>();
  const { name: pollName } = useCurrentPoll();
  const { isLoggedIn } = useLoginState();

  const { i18n, t } = useTranslation();
  const currentLang = i18n.resolvedLanguage;

  const [entity, setEntity] = useState<Recommendation>();
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState<ApiError>();
  const [pageTitle, setPageTitle] = useState(DEFAULT_DOCUMENT_TITLE);

  useDocumentTitle(pageTitle);

  useEffect(() => {
    if (entity) {
      const title = createPageTitle(t, pollName, entity.entity);
      if (title) {
        setPageTitle(title);
      }
    }
  }, [currentLang, entity, pollName, t]);

  const tryToCreateVideo = async () => {
    if (pollName !== YOUTUBE_POLL_NAME) {
      return false;
    }
    if (!isLoggedIn) {
      return false;
    }
    const videoId = extractVideoId(uid ?? '');
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
        uid: uid || '',
      });
      return entity;
    }

    async function getEntity(createVideo = true): Promise<void> {
      let reco: Recommendation | null = null;

      try {
        reco = await getEntityWithPollStats();
        setEntity(reco);
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
      <ContributorRatingContextProvider uid={uid}>
        {entity ? (
          <>
            {pollName === PRESIDENTIELLE_2022_POLL_NAME && (
              <CandidateAnalysisPage candidate={entity} />
            )}
            {pollName === YOUTUBE_POLL_NAME && (
              <VideoAnalysis entityResult={entity} />
            )}
          </>
        ) : (
          <Container>
            <Box
              sx={{
                py: 2,
              }}
            >
              <EntityNotFound apiError={apiError} />
            </Box>
          </Container>
        )}
      </ContributorRatingContextProvider>
    </LoaderWrapper>
  );
};

export default EntityAnalysisPage;
