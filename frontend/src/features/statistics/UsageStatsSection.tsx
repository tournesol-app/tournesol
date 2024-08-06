import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Tooltip, Typography } from '@mui/material';

import { useCurrentPoll, useStats } from 'src/hooks';
import { getPollStats } from './stats';
import SectionTitle from 'src/pages/home/videos/sections/SectionTitle';

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

  const stats = useStats({ poll: pollName });
  const pollStats = getPollStats(stats, pollName);

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
    <Box>
      <SectionTitle
        title={t('statsSection.statistics')}
        headingId="statistics"
      />
      <Box
        textAlign="center"
        width="100%"
        display="flex"
        justifyContent="center"
      >
        <Grid container sx={{ maxWidth: 1000 }}>
          <Grid item xs={12} sm={4}>
            <Metrics
              text={t('stats.activatedAccounts')}
              count={stats.active_users.total ?? 0}
              lastMonthCount={stats.active_users.joined_last_30_days ?? 0}
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
    </Box>
  );
};

export default StatsSection;
