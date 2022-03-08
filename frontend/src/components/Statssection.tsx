import { Grid } from '@mui/material';
import { StatsService } from 'src/services/openapi';
import type { Statistics } from 'src/services/openapi';
import React, { useEffect, useState } from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import Typography from '@mui/material/Typography';
import Box from '@mui/system/Box';

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

const StatsUi = ({ text, count, lastMonthCount }: statsProp) => {
  return (
    <Grid item xs={12} sm={4}>
      <Typography component="span" sx={{ fontSize: '24px' }}>
        {text}
      </Typography>
      <br />
      <Typography component="span" sx={{ fontSize: '50px', lineHeight: '1em' }}>
        {count}
      </Typography>
      <br />
      <Typography
        component="span"
        title={`New ${text} in the last month`}
        sx={{ fontSize: '24px' }}
      >
        + {lastMonthCount}
      </Typography>
    </Grid>
  );
};

const StatsSection = () => {
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
          lastMonthComparisonCount: value.last_month_video_count,
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  return (
    <Box
      sx={{
        background: '#1282B2',
        color: 'white',
        textAlign: 'center',
        py: 4,
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <Grid container sx={{ maxWidth: 800 }}>
        <StatsUi
          text="Active users"
          count={data.userCount}
          lastMonthCount={data.lastMonthUserCount}
        />
        <StatsUi
          text="Comparisons"
          count={data.comparisonCount}
          lastMonthCount={data.lastMonthComparisonCount}
        />
        <StatsUi
          text="Rated videos"
          count={data.videoCount}
          lastMonthCount={data.lastMonthVideoCount}
        />
      </Grid>
    </Box>
  );
};

export default StatsSection;
