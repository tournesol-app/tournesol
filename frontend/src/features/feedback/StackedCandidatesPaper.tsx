import React, { useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import {
  Avatar,
  Box,
  Button,
  Grid,
  Link,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Typography,
} from '@mui/material';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { useCurrentPoll } from 'src/hooks';
import {
  ContributorRating,
  ContributorRecommendations,
} from 'src/services/openapi';
import StackedCard from 'src/components/StackedCard';

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
  const { baseUrl, getCriteriaLabel } = useCurrentPoll();

  const allCriteria = new Set(
    recommendations.flatMap((entityScore) =>
      entityScore.criteria_scores.map((cs) => cs.criteria)
    )
  );

  const nComparisons = Object.fromEntries(
    ratings.map((rating) => {
      return [rating.entity.uid, rating.n_comparisons];
    })
  );

  const sortedRecommendations = recommendations
    .filter(
      (entityWithScores) =>
        entityWithScores.criteria_scores.find(
          ({ criteria }) => criteria == sortingCriteria
        )?.score
    )
    .map((entityWithScores) => ({
      entity: entityWithScores,
      score: entityWithScores.criteria_scores.find(
        ({ criteria }) => criteria == sortingCriteria
      )?.score,
    }))
    .map(({ entity, score }) => ({ entity, score: 10 * (score as number) }))
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
      items={sortedRecommendations.map(({ entity, score }) => {
        const nComp = nComparisons[entity.uid] || 0;
        return (
          <ListItem key={entity.uid} alignItems="flex-start">
            <ListItemAvatar>
              <Avatar
                alt={entity?.metadata?.name || ''}
                src={entity?.metadata?.image_url || ''}
              />
            </ListItemAvatar>
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
                    <Link
                      color="inherit"
                      component={RouterLink}
                      to={`${baseUrl}/comparisons/?uid=${entity.uid}`}
                    >
                      <Trans
                        t={t}
                        i18nKey="stackedCandidatesPaper.withNComparisons"
                        count={nComp}
                      >
                        with {{ nComp }} comparisons
                      </Trans>
                    </Link>
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
            <Select
              fullWidth
              color="secondary"
              size="small"
              value={sortingCriteria}
              onChange={(v) => setSortingCriteria(v.target.value)}
            >
              {[...allCriteria].map((criteria) => (
                <MenuItem key={criteria} value={criteria}>
                  {getCriteriaLabel(criteria)}
                </MenuItem>
              ))}
            </Select>
          </Box>
          <Box pt={2} pb={1} px={2}>
            <Typography paragraph variant="body2" textAlign="justify">
              {t('stackedCandidatesPaper.ifYourRankingSeemsOff')}
            </Typography>
          </Box>
          <Grid container>
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
          </Grid>
        </>
      }
    />
  );
};

export default StackedCandidatesPaper;
