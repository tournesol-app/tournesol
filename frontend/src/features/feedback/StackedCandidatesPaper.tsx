import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import {
  Avatar,
  Box,
  Button,
  Grid,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Typography,
} from '@mui/material';

import { InternalLink } from 'src/components';
import StackedCard from 'src/components/StackedCard';
import { useCurrentPoll } from 'src/hooks';
import {
  ContributorRating,
  ContributorRecommendations,
} from 'src/services/openapi';
import CriteriaSelector from 'src/features/criteria/CriteriaSelector';

interface Props {
  comparisonsNbr: number;
  ratings: ContributorRating[];
  recommendations: ContributorRecommendations[];
}

/**
 * Display an ordered list of candidates, with their total score and their
 * number of comparisons.
 */
const StackedCandidatesPaper = ({
  comparisonsNbr,
  ratings,
  recommendations,
}: Props) => {
  const [sortingCriteria, setSortingCriteria] = useState('be_president');
  const { t } = useTranslation();
  const { active, baseUrl } = useCurrentPoll();

  const nComparisons = Object.fromEntries(
    ratings.map((rating) => {
      return [rating.entity.uid, rating.individual_rating.n_comparisons];
    })
  );

  const sortedRecommendations = recommendations
    .filter(
      (entityWithScores) =>
        entityWithScores.individual_rating.criteria_scores.find(
          ({ criteria }) => criteria == sortingCriteria
        )?.score != null
    )
    .map((entityWithScores) => ({
      reco: entityWithScores,
      score: entityWithScores.individual_rating.criteria_scores.find(
        ({ criteria }) => criteria == sortingCriteria
      )?.score,
    }))
    .map(({ reco, score }) => ({ reco, score: 10 * (score as number) }))
    .sort((a, b) => (a.score < b.score ? 1 : -1));

  return (
    <StackedCard
      title={
        <Typography variant="h5">
          <Trans
            t={t}
            i18nKey="stackedCandidatesPaper.title"
            count={comparisonsNbr}
          >
            Should be president according to your {{ comparisonsNbr }}{' '}
            comparisons
          </Trans>
        </Typography>
      }
      items={sortedRecommendations.map(({ reco, score }) => {
        const entity = reco.entity;
        const nComp = nComparisons[entity.uid] || 0;
        return (
          <ListItem key={entity.uid} alignItems="flex-start">
            <ListItemAvatar>
              <InternalLink to={`${baseUrl}/entities/${entity.uid}`}>
                <Avatar
                  alt={entity?.metadata?.name || ''}
                  src={entity?.metadata?.image_url || ''}
                />
              </InternalLink>
            </ListItemAvatar>

            {/* To stay mobile friendly, only the avatar is clickable. The
                primary text is too close to the comparisons link, making it
                clickalbe makes it easy to click on the wrong link. */}
            <ListItemText
              primary={entity?.metadata?.name || '??'}
              secondary={
                <>
                  <Typography
                    sx={{ display: 'inline' }}
                    component="span"
                    variant="body2"
                    color="text.primary"
                  >
                    <InternalLink
                      color="inherit"
                      to={`${baseUrl}/comparisons/?uid=${entity.uid}`}
                    >
                      <Trans
                        t={t}
                        i18nKey="stackedCandidatesPaper.withNComparisons"
                        count={nComp}
                      >
                        with {{ nComp }} comparisons
                      </Trans>
                    </InternalLink>
                  </Typography>
                  {' - '}
                  {t('stackedCandidatesPaper.score')}
                  {' ' + score.toFixed(2)}
                </>
              }
            />
          </ListItem>
        );
      })}
      actions={
        <>
          <Box pt={2} pb={1} px={2}>
            <Typography>{t('stackedCandidatesPaper.onCriteria')}</Typography>
            <CriteriaSelector
              criteria={sortingCriteria}
              setCriteria={setSortingCriteria}
            />
          </Box>
          <Box pt={2} pb={1} px={2}>
            <Typography paragraph variant="body2" textAlign="justify">
              {t('stackedCandidatesPaper.ifYourRankingSeemsOff')}
            </Typography>
          </Box>
          <Grid container justifyContent="flex-end">
            <Grid item xs={6} sx={{ px: 1 }}>
              <Button
                color="secondary"
                variant="outlined"
                component={RouterLink}
                to={`${baseUrl}/comparisons`}
                sx={{ height: '100%' }}
                fullWidth
              >
                {t('stackedCandidatesPaper.seeMyComparisons')}
              </Button>
            </Grid>
            {active && (
              <Grid item xs={6} sx={{ px: 1 }}>
                <Button
                  color="secondary"
                  component={RouterLink}
                  variant="contained"
                  to={`${baseUrl}/comparison`}
                  sx={{ height: '100%' }}
                  fullWidth
                >
                  {t('stackedCandidatesPaper.addNewComparisons')}
                </Button>
              </Grid>
            )}
          </Grid>
        </>
      }
    />
  );
};

export default StackedCandidatesPaper;
