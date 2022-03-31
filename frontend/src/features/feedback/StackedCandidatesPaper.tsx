import React from 'react';
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
  recommendations: ContributorRecommendations[];
}

const StackedCandidatesPaper = ({ recommendations }: Props) => {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h5">
        Should be president according to your X comparisons
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
                primary={reco?.metadata?.name || 'Aucun nom'}
                secondary={
                  <React.Fragment>
                    <Typography
                      sx={{ display: 'inline' }}
                      component="span"
                      variant="body2"
                      color="text.primary"
                    >
                      with 3 comparisons
                    </Typography>
                    {' - score '}
                    {reco.total_score.toFixed(2)}
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
