import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Grid, Tooltip, Typography } from '@mui/material';
import { Statistics, StatsService } from 'src/services/openapi';

interface statsProp {
  text: string;
  count: number;
  lastMonthCount: number;
}

interface statsData {
  userCount: number;
  lastMonthUserCount: number;
  videoCount: number;
  lastMonthVideoCount: number;
  comparisonCount: number;
  lastMonthComparisonCount: number;
}

const Metrics = ({ text, count, lastMonthCount }: statsProp) => {
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
    </>
  );
};

const StatsSection = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<statsData>({
    userCount: 0,
    lastMonthUserCount: 0,
    videoCount: 0,
    lastMonthVideoCount: 0,
    comparisonCount: 0,
    lastMonthComparisonCount: 0,
  });

  useEffect(() => {
    StatsService.statsRetrieve()
      .then((value: Statistics) => {
        setData({
          userCount: value.user_count,
          videoCount: value.video_count,
          comparisonCount: value.comparison_count,
          lastMonthUserCount: value.last_month_user_count,
          lastMonthVideoCount: value.last_month_video_count,
          lastMonthComparisonCount: value.last_month_comparison_count,
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  return (
    <Box
      sx={{
        textAlign: 'center',
        py: 4,
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <Grid container sx={{ maxWidth: 1000 }}>
        <Grid item xs={12} sm={4}>
          <Metrics
            text={t('stats.activeUsers')}
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
            text={t('stats.ratedVideos')}
            count={data.videoCount}
            lastMonthCount={data.lastMonthVideoCount}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default StatsSection;
