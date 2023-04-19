import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';

import { Box, Grid, Tooltip, Typography } from '@mui/material';

import { selectStats } from 'src/features/comparisons/statsSlice';
import { useCurrentPoll } from 'src/hooks';

interface statsProp {
  text: string;
  count: number;
  lastMonthCount: number;
  // Add an explanation text after `lastMonthCount`.
  lastMonthAsText?: boolean;
}

export const Metrics = ({
  text,
  count,
  lastMonthCount,
  lastMonthAsText = false,
}: statsProp) => {
  const { i18n, t } = useTranslation();
  const tooltipTitle = t('metrics.evolutionDuringTheLast30Days');

  return (
    <>
      <Typography component="span" sx={{ fontSize: '24px' }}>
        {text}
      </Typography>
      <br />
      <Typography component="span" sx={{ fontSize: '50px', lineHeight: '1em' }}>
        {count.toLocaleString(i18n.resolvedLanguage)}
      </Typography>
      <br />
      <Tooltip title={tooltipTitle}>
        <Typography component="span" sx={{ fontSize: '24px' }}>
          + {lastMonthCount.toLocaleString(i18n.resolvedLanguage)}
        </Typography>
      </Tooltip>
      {lastMonthAsText && (
        <Typography component="span">
          &nbsp;{t('metrics.duringTheLast30Days')}
        </Typography>
      )}
    </>
  );
};

/**
 * Display the Tournesol main statistics.
 *
 * If `externalData` is provided, the component displays it instead of
 * retrieving the data from the API.
 */
const StatsSection = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const publicStats = useSelector(selectStats);

  const pollStats = publicStats.polls.find((poll) => {
    if (poll.name === pollName) {
      return poll;
    }
  });

  const comparedEntitiesTitle = useMemo(() => {
    switch (pollName) {
      case 'videos':
        return t('stats.ratedVideos');
      case 'presidentielle2022':
        return t('stats.ratedCandidates');
      default:
        throw new Error(`Unknown poll: ${pollName}`);
    }
  }, [pollName, t]);

  return (
    <Box
      sx={{
        textAlign: 'center',
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <Grid container sx={{ maxWidth: 1000 }}>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={t('stats.activatedAccounts')}
            count={publicStats.active_users.total}
            lastMonthCount={publicStats.active_users.joined_last_30_days}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={t('stats.comparisons')}
            count={pollStats?.comparisons.total ?? 0}
            lastMonthCount={pollStats?.comparisons.added_last_30_days ?? 0}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={comparedEntitiesTitle}
            count={pollStats?.compared_entities.total ?? 0}
            lastMonthCount={
              pollStats?.compared_entities.added_last_30_days ?? 0
            }
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default StatsSection;
