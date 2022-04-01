import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import {
  Avatar,
  Divider,
  Link,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';
import { useCurrentPoll } from 'src/hooks';
import {
  ContributorRating,
  ContributorRecommendations,
} from 'src/services/openapi';

interface Props {
  comparisonsNbr: number;
  ratings: ContributorRating[];
  recommendations: ContributorRecommendations[];
}

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
    <Paper sx={{ p: 2 }}>
      <Typography
        variant="h5"
        sx={{ color: '#fff', backgroundColor: '#1282B2' }}
      >
        <Trans t={t} i18nKey="stackedCandidatesPaper.title">
          Should be president according to your {{ comparisonsNbr }} comparisons
        </Trans>
      </Typography>
      <List>
        {recommendations.map((reco) => {
          const nComp = nComparisons[reco.uid] || 0;
          return (
            <>
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
                    <React.Fragment>
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
                          >
                            with {{ nComp }} comparisons
                          </Trans>
                        </Link>
                      </Typography>
                      {' - '}
                      {t('stackedCandidatesPaper.score')}
                      {' ' + reco.total_score.toFixed(2)}
                    </React.Fragment>
                  }
                />
              </ListItem>
              <Divider variant="inset" component="li" />
            </>
          );
        })}
      </List>
    </Paper>
  );
};

export default StackedCandidatesPaper;
