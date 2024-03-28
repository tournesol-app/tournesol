import React, { useEffect, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
} from '@mui/material';
import { ExternalLink, LoaderWrapper } from 'src/components';
import StackedCandidatesPaper from 'src/features/feedback/StackedCandidatesPaper';
import StackedCriteriaPaper from 'src/features/feedback/StackedCriteriaPaper';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { getUserComparisons } from 'src/utils/api/comparisons';
import {
  ContributorRating,
  ContributorRecommendations,
  PollCriteria,
  UsersService,
} from 'src/services/openapi';
import {
  getPollName,
  polls,
  PRESIDENTIELLE_2022_SURVEY_URL,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { SelectablePoll } from 'src/utils/types';
import ProofOfVote from './ProofOfVote';

const COMPARISONS_NBR_MAX = 100;

const FeedbackPagePresidentielle2022 = () => {
  const { t } = useTranslation();
  const { baseUrl, criterias, name: pollName, options } = useCurrentPoll();
  const videoPoll = polls.find(
    (poll) => poll.name === YOUTUBE_POLL_NAME
  ) as SelectablePoll;

  const [isLoading, setIsLoading] = useState(true);
  const [comparisonsNbr, setComparisonsNbr] = useState(0);

  const [criteriaCorrelations, setCriteriaCorrelations] = useState<{
    criteria: string[];
    correlations: Array<number | null>;
  }>({ criteria: [], correlations: [] });
  const [ratings, setRatings] = useState<ContributorRating[]>([]);
  const [recommendations, setRecommendations] = useState<
    Array<ContributorRecommendations>
  >([]);

  const minComparisons = options?.tutorialLength || 7;
  const remainingComparisons = minComparisons - comparisonsNbr;

  const weightRecommendationCriteria = (criteria: PollCriteria[]) => {
    const weights = Object.fromEntries(
      criteria.map((criterion) => [criterion.name, 0])
    );
    weights.be_president = 10;

    return weights;
  };

  useEffect(() => {
    // ratings are used to know how many times a candidate has been compared
    async function getUserRatings(): Promise<ContributorRating[]> {
      const ratings = await UsersService.usersMeContributorRatingsList({
        pollName: pollName,
      });
      return ratings.results || [];
    }

    // used to display an ordered list of criteria
    async function getUserCriteriaCorrelation() {
      const correlationsObj =
        await UsersService.usersMeCriteriaCorrelationsRetrieve({
          pollName: pollName,
        });

      const criteria = correlationsObj.criterias || [];

      const correlations =
        correlationsObj.correlations && correlationsObj.correlations.length > 0
          ? [...correlationsObj.correlations[0]]
          : [];

      return { criteria, correlations };
    }

    // used to display an ordered list of candidates, according to be_president
    async function getUserRecommendations(): Promise<
      ContributorRecommendations[]
    > {
      const reco = await UsersService.usersMeRecommendationsList({
        pollName: pollName,
        unsafe: true,
        weights: weightRecommendationCriteria(criterias),
      });

      return reco.results || [];
    }

    const ratingsPromise = getUserRatings();
    const criteriaCorrelationPromise = getUserCriteriaCorrelation();
    const recommendationsPromise = getUserRecommendations();
    const comparisonsPromise = getUserComparisons(
      pollName,
      COMPARISONS_NBR_MAX
    );

    Promise.all([
      ratingsPromise,
      criteriaCorrelationPromise,
      recommendationsPromise,
      comparisonsPromise,
    ]).then(
      ([
        contributorRatings,
        criteriaCorrelation,
        contributorRecommendation,
        comparisons,
      ]) => {
        setComparisonsNbr(comparisons.length);
        setCriteriaCorrelations(criteriaCorrelation);
        setRatings(contributorRatings);
        setRecommendations(contributorRecommendation);
        setIsLoading(false);
      }
    );
  }, [criterias, pollName]);

  return (
    <>
      <LoaderWrapper isLoading={isLoading}>
        {comparisonsNbr < minComparisons ? (
          <>
            <Typography variant="h2" textAlign="center">
              {t('myFeedbackPage.presidentielle2022.welcomeOnYourResultPage')}
            </Typography>
            <Typography paragraph mt={2} textAlign="justify">
              <Trans
                t={t}
                i18nKey="myFeedbackPage.presidentielle2022.notEnoughComparisons"
                count={remainingComparisons}
              >
                We need at least {{ minComparisons }} different comparisons
                before being able to display your results.{' '}
                {{ remainingComparisons }} comparisons are still required. Click
                on the button below, and follow the instructions to continue.
              </Trans>
            </Typography>
            <Box mt={2} display="flex" justifyContent="center">
              <Button
                variant="contained"
                component={RouterLink}
                to={`${baseUrl}/comparison`}
              >
                {t('myFeedbackPage.presidentielle2022.continueComparisons')}
              </Button>
            </Box>
          </>
        ) : (
          <>
            <Typography variant="h3" textAlign="center">
              {t(
                'myFeedbackPage.presidentielle2022.thanksForComparingCandidates'
              )}
            </Typography>
            <ProofOfVote
              label={t('myFeedbackPage.proofOfVote')}
              helperText={
                <Trans t={t} i18nKey="myFeedbackPage.proofOfVoteHelperText">
                  This code will be helpful to complete{' '}
                  <ExternalLink href={PRESIDENTIELLE_2022_SURVEY_URL}>
                    our survey.
                  </ExternalLink>
                </Trans>
              }
            />
            <Typography paragraph textAlign="right">
              <Button
                color="secondary"
                variant="contained"
                component={RouterLink}
                to={`${baseUrl}/recommendations`}
              >
                {t('myFeedbackPage.presidentielle2022.goToGlobalRanking')}
              </Button>
            </Typography>
            <Grid
              container
              spacing={2}
              justifyContent="center"
              textAlign="center"
            >
              <Grid item xs={12} sm={12} md={6}>
                <StackedCriteriaPaper
                  criteriaCorrelations={criteriaCorrelations}
                />
              </Grid>
              <Grid item xs={12} sm={12} md={6}>
                <StackedCandidatesPaper
                  comparisonsNbr={comparisonsNbr}
                  ratings={ratings}
                  recommendations={recommendations}
                />
              </Grid>
              <Grid item textAlign="left">
                <Card>
                  <CardHeader
                    sx={{
                      color: '#000',
                      backgroundColor: '#eee',
                      p: 1,
                      textAlign: 'center',
                    }}
                    title={t('myFeedbackPage.generic.whatsNext')}
                  />
                  <CardContent>
                    <Typography paragraph>
                      {t(
                        'myFeedbackPage.presidentielle2022.opinionsOnOnlineSharedContent'
                      )}
                    </Typography>
                    <Typography paragraph>
                      {t(
                        'myFeedbackPage.presidentielle2022.discoverTournesolVideos'
                      )}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Button
                        color="secondary"
                        component={RouterLink}
                        to={videoPoll.path}
                        variant="outlined"
                        startIcon={<videoPoll.iconComponent />}
                        sx={{ height: '100%' }}
                      >
                        {t('myFeedbackPage.generic.discoverTournesol')}{' '}
                        {getPollName(t, videoPoll.name)}
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </>
        )}
      </LoaderWrapper>
    </>
  );
};

export default FeedbackPagePresidentielle2022;
