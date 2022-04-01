import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Grid, Paper, Typography } from '@mui/material';
import StackedCandidatesPaper from 'src/features/feedback/StackedCandidatesPaper';
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
  const { name: pollName, criterias } = useCurrentPoll();

  const [comparisonsNbr, setComparisonsNbr] = useState(0);
  const [ratings, setRatings] = useState<ContributorRating[]>([]);
  const [recommendations, setRecommendations] = useState<
    Array<ContributorRecommendations>
  >([]);

  const weightRecommendationCriteria = (criteria: PollCriteria[]) => {
    const weights = Object.fromEntries(
      criteria.map((criterion) => [criterion.name, 0])
    );
    weights.be_president = 10;

    return weights;
  };

  useEffect(() => {
    async function getUserRatings(): Promise<ContributorRating[]> {
      const ratings = await UsersService.usersMeContributorRatingsList({
        pollName: pollName,
      });
      return ratings.results || [];
    }

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
    const recommendationsPromise = getUserRecommendations();
    const comparisonsPromise = getUserComparisons(
      pollName,
      COMPARISONS_NBR_MAX
    );

    Promise.all([
      ratingsPromise,
      recommendationsPromise,
      comparisonsPromise,
    ]).then(([contributorRatings, contributorRecommendation, comparisons]) => {
      setComparisonsNbr(comparisons.length);
      setRatings(contributorRatings);
      setRecommendations(contributorRecommendation);
    });
  }, [criterias, pollName]);

  return (
    <>
      <Typography variant="h2" textAlign="center">
        {t('myFeedbackPage.presidentielle2022.subtitle')}
      </Typography>
      <Typography paragraph mt={2} textAlign="justify">
        {t('myFeedbackPage.presidentielle2022.description')}
      </Typography>
      <Grid container spacing={2} textAlign="center">
        <Grid item xs={12} sm={12} md={6}>
          <Paper sx={{ height: '300px' }}>WIP</Paper>
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
  );
};

export default FeedbackPagePresidentielle2022;
