import { Grid } from '@mui/material';
import { StatsService } from 'src/services/openapi';
import type { Statistics } from 'src/services/openapi';
import React, { useEffect, useState } from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import { Box } from '@mui/system';

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

const StatsUi = (props: statsProp) => {
  return (
    <Grid item xs={4}>
      <Box component="span" sx={{ fontSize: '12px' }}>
        {props.text}
      </Box>{' '}
      <br />
      <Box component="span" sx={{ fontSize: '50px', lineHeight: '1em' }}>
        {' '}
        {props.count}{' '}
      </Box>{' '}
      <br />
      {
        <Box
          component="span"
          sx={props.lastMonthCount >= 0 ? { color: 'black' } : { color: 'red' }}
        >
          {(props.lastMonthCount >= 0 ? '+ ' : '') + props.lastMonthCount}
        </Box>
      }
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

  const matches = useMediaQuery('(min-width:600px)');

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
    <Grid
      container
      sx={{ background: '#1282B2', color: 'white', textAlign: 'center' }}
      direction={!matches ? 'column' : 'row'}
    >
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
  );
};

export default StatsSection;
