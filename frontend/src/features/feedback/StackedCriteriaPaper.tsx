import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import {
  Box,
  Button,
  Grid,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Typography,
} from '@mui/material';
import { criteriaToEmoji } from 'src/utils/constants';
import { useCurrentPoll } from 'src/hooks';
import StackedCard from 'src/components/StackedCard';

interface Props {
  criteriaCorrelations: {
    criteria: string[];
    correlations: Array<number | null>;
  };
}

const CriteriaCorrelationListItem = (correlation: {
  criterion: string;
  value: number;
}) => {
  const { getCriteriaLabel } = useCurrentPoll();

  return (
    <ListItem key={correlation.criterion} alignItems="flex-start">
      <ListItemAvatar
        sx={{
          fontSize: '30px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        {criteriaToEmoji[correlation.criterion]}
      </ListItemAvatar>
      <ListItemText
        primary={getCriteriaLabel(correlation.criterion)}
        secondary={`Coefficient de correlation ${correlation.value.toFixed(2)}`}
      />
    </ListItem>
  );
};

/**
 * Display an ordered list of candidates, with their total score and their
 * number of comparisons.
 */
const StackedCriteriaPaper = ({ criteriaCorrelations }: Props) => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();

  const orderedCriteriaCorrelations = criteriaCorrelations.criteria
    .map((criterion, idx) => {
      return {
        criterion: criterion,
        value: criteriaCorrelations.correlations[idx] || -100, // TODO change this default of -100
      };
    })
    .filter(({ criterion }) => criterion != 'be_president')
    .sort((a, b) => {
      if (a.value < b.value) {
        return 1;
      }
      if (a.value > b.value) {
        return -1;
      }
      return 0;
    });

  return (
    <StackedCard
      title={
        <Typography variant="h5">
          {/* TODO Add translation*/}
          Criteria most correlated to who you think should be president
        </Typography>
      }
      items={orderedCriteriaCorrelations.map((correlation) => (
        <CriteriaCorrelationListItem
          key={correlation.criterion}
          {...correlation}
        />
      ))}
      actions={
        <>
          <Box pt={2} pb={1} px={2}>
            <Typography paragraph variant="body2" textAlign="justify">
              If these results seem off to you, you can either modify your
              existing comparisons or make new comparisons. Otherwise we welcome
              you to share your experience on Twitter
            </Typography>
          </Box>
          <Grid container spacing={1}>
            <Grid item xs={6} sx={{ px: 1 }}>
              <Button
                color="secondary"
                component={RouterLink}
                variant="outlined"
                to={`${baseUrl}/comparison`}
                sx={{ height: '100%' }}
                fullWidth
              >
                {t('stackedCandidatesPaper.addNewComparisons')}
              </Button>
            </Grid>
            <Grid item xs={6} sx={{ px: 1 }}>
              <Button
                color="secondary"
                onClick={() => 'TODO'}
                variant="contained"
                sx={{ height: '100%' }}
                fullWidth
              >
                Share On Twitter
              </Button>
            </Grid>
          </Grid>
        </>
      }
    />
  );
};

export default StackedCriteriaPaper;
