import React from 'react';
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
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();

  const nComparisons = Object.fromEntries(
    ratings.map((rating) => {
      return [rating.entity.uid, rating.n_comparisons];
    })
  );

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
      items={recommendations.map((reco) => {
        const nComp = nComparisons[reco.uid] || 0;
        return (
          <ListItem key={reco.uid} alignItems="flex-start">
            <ListItemAvatar>
              <Avatar
                alt={reco?.metadata?.name || ''}
                src={reco?.metadata?.image_url || ''}
              />
            </ListItemAvatar>
            <ListItemText
              primary={reco?.metadata?.name || '??'}
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
                      to={`${baseUrl}/comparisons/?uid=${reco.uid}`}
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
                  {' ' + reco.total_score.toFixed(2)}
                </>
              }
            />
          </ListItem>
        );
      })}
      actions={
        <>
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
