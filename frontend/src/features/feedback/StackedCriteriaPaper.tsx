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
import { Twitter } from '@mui/icons-material';
import { criteriaToEmoji } from 'src/utils/constants';
import { useCurrentPoll } from 'src/hooks';
import StackedCard from 'src/components/StackedCard';
import { openTwitterPopup } from 'src/utils/ui';

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
  const { t } = useTranslation();
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
        secondary={`${t(
          'stackedCriteriaPaper.score'
        )} ${correlation.value.toFixed(2)}`}
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
  const { active, baseUrl } = useCurrentPoll();

  const orderedCriteriaCorrelations = criteriaCorrelations.criteria
    .map((criterion, idx) => {
      return {
        criterion: criterion,
        value: criteriaCorrelations.correlations[idx],
      };
    })
    .filter(({ criterion }) => criterion != 'be_president')
    .filter(({ value }) => value != null)
    .map(({ value, criterion }) => ({ criterion, value: value as number }))
    .sort((a, b) => {
      if (b.value === a.value) return 0;
      return a.value < b.value ? 1 : -1;
    });

  const getTweet = () => {
    const getEmojis = (correlation: { criterion: string; value: number }) => {
      const nbEmojis = Math.max(1, 1 + correlation.value / 0.2);
      return criteriaToEmoji[correlation.criterion].repeat(nbEmojis);
    };
    const emojis = orderedCriteriaCorrelations.slice(0, 3).map(getEmojis);
    return (
      `${t('stackedCriteriaPaper.tweet.intro')}\n${emojis.join('\n')}\n\n` +
      `${t('stackedCriteriaPaper.tweet.conclusion')}` +
      `🌻\nhttps://tournesol.app${baseUrl}`
    );
  };

  return (
    <StackedCard
      title={
        <Typography variant="h5">{t('stackedCriteriaPaper.title')}</Typography>
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
              {t('stackedCriteriaPaper.ifYourRankingSeemsOff')}
            </Typography>
          </Box>
          <Grid container spacing={1} justifyContent="flex-end">
            {active && (
              <Grid item xs={6} sx={{ px: 1 }}>
                <Button
                  color="secondary"
                  component={RouterLink}
                  variant="outlined"
                  to={`${baseUrl}/comparison`}
                  sx={{ height: '100%' }}
                  fullWidth
                >
                  {t('stackedCriteriaPaper.addNewComparisons')}
                </Button>
              </Grid>
            )}
            <Grid item xs={6} sx={{ px: 1 }}>
              <Button
                color="secondary"
                onClick={() => openTwitterPopup(getTweet())}
                variant="contained"
                sx={{ height: '100%' }}
                startIcon={<Twitter />}
                fullWidth
              >
                {t('stackedCriteriaPaper.shareOnTwitter')}
              </Button>
            </Grid>
          </Grid>
        </>
      }
    />
  );
};

export default StackedCriteriaPaper;
