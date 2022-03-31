import React from 'react';
import { Trans, useTranslation } from 'react-i18next';
import {
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';
import { ContributorRecommendations } from 'src/services/openapi';

interface Props {
  comparisonsNbr: number;
  recommendations: ContributorRecommendations[];
}

const StackedCandidatesPaper = ({ comparisonsNbr, recommendations }: Props) => {
  const { t } = useTranslation();

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
        {recommendations.map((reco) => (
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
                      <Trans
                        t={t}
                        i18nKey="stackedCandidatesPaper.withNComparisons"
                      >
                        with X comparisons
                      </Trans>
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
        ))}
      </List>
    </Paper>
  );
};

export default StackedCandidatesPaper;
