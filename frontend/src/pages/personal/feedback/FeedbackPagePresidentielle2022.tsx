import React, { useEffect, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Box, Button, Grid, Typography } from '@mui/material';
import { LoaderWrapper } from 'src/components';
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

const COMPARISONS_NBR_MAX = 100;

const FeedbackPagePresidentielle2022 = () => {
  const { t } = useTranslation();
  const { baseUrl, criterias, name: pollName, options } = useCurrentPoll();

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
                component={Link}
                to={`${baseUrl}/comparison?series=true`}
              >
                {t('myFeedbackPage.presidentielle2022.continueComparisons')}
              </Button>
            </Box>
          </>
        ) : (
          <>
            <Typography variant="h2" textAlign="center">
              {t(
                'myFeedbackPage.presidentielle2022.thanksForComparingCandidates'
              )}
            </Typography>
            <Typography paragraph mt={2} textAlign="justify">
              {t('myFeedbackPage.presidentielle2022.description')}
            </Typography>
            <Grid container spacing={2} textAlign="center">
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
            </Grid>
          </>
        )}
      </LoaderWrapper>
    </>
  );
};

export default FeedbackPagePresidentielle2022;
