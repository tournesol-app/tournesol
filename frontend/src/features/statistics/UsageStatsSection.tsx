import React, { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Grid, Tooltip, Typography } from '@mui/material';

import { useCurrentPoll } from 'src/hooks';
import { getPollStats } from 'src/utils/api/stats';
import { PollStats } from 'src/utils/types';

interface statsProp {
  text: string;
  count: number;
  lastMonthCount: number;
  verbose?: boolean;
}

interface StatsSectionProps {
  externalData?: PollStats;
}

export const Metrics = ({
  text,
  count,
  lastMonthCount,
  verbose = false,
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
      {verbose && (
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
const StatsSection = ({ externalData }: StatsSectionProps) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const [data, setData] = useState<PollStats>({
    userCount: 0,
    lastMonthUserCount: 0,
    comparedEntityCount: 0,
    lastMonthComparedEntityCount: 0,
    comparisonCount: 0,
    lastMonthComparisonCount: 0,
  });

  useEffect(() => {
    async function getPollStatsAsync(pollName: string) {
      try {
        const pollStats = await getPollStats(pollName);
        if (pollStats) {
          setData(pollStats);
        }
      } catch (reason) {
        console.error(reason);
      }
    }

    if (!externalData) {
      getPollStatsAsync(pollName);
    }
  }, [externalData, pollName]);

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
            count={externalData?.userCount || data.userCount}
            lastMonthCount={
              externalData?.lastMonthUserCount || data.lastMonthUserCount
            }
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={t('stats.comparisons')}
            count={externalData?.comparisonCount || data.comparisonCount}
            lastMonthCount={
              externalData?.lastMonthComparisonCount ||
              data.lastMonthComparisonCount
            }
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={comparedEntitiesTitle}
            count={
              externalData?.comparedEntityCount || data.comparedEntityCount
            }
            lastMonthCount={
              externalData?.lastMonthComparedEntityCount ||
              data.lastMonthComparedEntityCount
            }
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default StatsSection;
