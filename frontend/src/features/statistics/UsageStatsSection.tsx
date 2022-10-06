import React, { useEffect, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Grid, Tooltip, Typography } from '@mui/material';
import { Statistics, StatsService } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks';

interface statsProp {
  text: string;
  count: number;
  lastMonthCount: number;
  verbose?: boolean;
}

interface statsData {
  userCount: number;
  lastMonthUserCount: number;
  comparedEntityCount: number;
  lastMonthComparedEntityCount: number;
  comparisonCount: number;
  lastMonthComparisonCount: number;
}

export const Metrics = ({
  text,
  count,
  lastMonthCount,
  verbose = false,
}: statsProp) => {
  const { t } = useTranslation();
  const tooltipTitle = t('metrics.evolutionDuringTheLast30Days');

  return (
    <>
      <Typography component="span" sx={{ fontSize: '24px' }}>
        {text}
      </Typography>
      <br />
      <Typography component="span" sx={{ fontSize: '50px', lineHeight: '1em' }}>
        {count}
      </Typography>
      <br />
      <Tooltip title={tooltipTitle}>
        <Typography component="span" sx={{ fontSize: '24px' }}>
          + {lastMonthCount}
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

const StatsSection = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<statsData>({
    userCount: 0,
    lastMonthUserCount: 0,
    comparedEntityCount: 0,
    lastMonthComparedEntityCount: 0,
    comparisonCount: 0,
    lastMonthComparisonCount: 0,
  });
  const { name: pollName } = useCurrentPoll();

  useEffect(() => {
    StatsService.statsRetrieve()
      .then((value: Statistics) => {
        const pollStats = value.polls.find(({ name }) => name === pollName);
        if (pollStats === undefined) return;
        setData({
          userCount: value.active_users.total,
          comparedEntityCount: pollStats.compared_entities.total,
          comparisonCount: pollStats.comparisons.total,
          lastMonthUserCount: value.active_users.joined_last_month,
          lastMonthComparedEntityCount:
            pollStats.compared_entities.added_last_month,
          lastMonthComparisonCount: pollStats.comparisons.added_last_month,
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }, [pollName]);

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
            count={data.userCount}
            lastMonthCount={data.lastMonthUserCount}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={t('stats.comparisons')}
            count={data.comparisonCount}
            lastMonthCount={data.lastMonthComparisonCount}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={comparedEntitiesTitle}
            count={data.comparedEntityCount}
            lastMonthCount={data.lastMonthComparedEntityCount}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default StatsSection;
