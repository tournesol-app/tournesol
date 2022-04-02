import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Divider,
  Grid,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';
import { criteriaToEmoji } from 'src/utils/constants';

interface Props {
  criteriaSlopes: {
    criteria: string[];
    slopes: Array<number | null>;
  };
}

/**
 * Display an ordered list of candidates, with their total score and their
 * number of comparisons.
 */
const StackedCriteriaPaper = ({ criteriaSlopes }: Props) => {
  const { t } = useTranslation();

  // XXX
  // should criterion be_president removed?
  const orderedSlopes = criteriaSlopes.criteria
    .map((criterion, idx) => {
      return {
        criterion: criterion,
        slope: criteriaSlopes.slopes[idx] || -100,
      };
    })
    .sort((a, b) => {
      if (a < b) {
        return -1;
      }
      if (a > b) {
        return 1;
      }
      return 0;
    });

  return (
    <Paper sx={{ p: 2 }}>
      <Typography
        variant="h5"
        sx={{ color: '#fff', backgroundColor: '#1282B2' }}
      >
        {/* XXX this is not correct, reword this */}
        Most important criteria according to you
      </Typography>
      <List>
        {orderedSlopes.map((slope) => {
          return (
            <>
              <ListItem key={slope.criterion} alignItems="flex-start">
                <ListItemAvatar>
                  {criteriaToEmoji[slope.criterion]}
                </ListItemAvatar>
                <ListItemText primary={slope.criterion} />
              </ListItem>
              <Divider variant="inset" component="li" />
            </>
          );
        })}
      </List>
      <Grid
        container
        spacing={2}
        justifyContent="center"
        sx={{ color: 'secondary.main' }}
      >
        <Grid item xs={6}></Grid>
        <Grid item xs={6}></Grid>
      </Grid>
    </Paper>
  );
};

export default StackedCriteriaPaper;
