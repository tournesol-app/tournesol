import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Container, Typography } from '@mui/material';

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

/**
 * TODO:
 *
 * - display a concise title
 * - display a paragraph containing a comprehensive description
 * - translate the title and the paragraph
 */
const EntityNotFound = ({ apiError }: { apiError: ApiError | undefined }) => {
  if (apiError == undefined) {
    return null;
  }

  let title: string;

  switch (apiError.status) {
    case 404:
      title = 'Not Found';
      break;
    default:
      title = 'Error';
  }

  return <Typography variant="h3">{title}</Typography>;
  title;
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
