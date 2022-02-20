import { Grid } from '@mui/material';
import { StatsService } from 'src/services/openapi';
import type { Statistics } from 'src/services/openapi';
import React, { useEffect, useState } from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';

interface statsType {
  text: string;
  count: number;
  last_month_count: number;
}

const StatsUi = (props: statsType) => {
  return (
    <Grid item xs={4}>
      <span style={{ fontSize: '12px' }}>{props.text}</span> <br />
      <span style={{ fontSize: '50px', lineHeight: '1em' }}>
        {' '}
        {props.count}{' '}  
      </span>{' '}
      <br />
      {
        <span
          style={
            props.last_month_count >= 0 ? { color: 'green' } : { color: 'red' }
          }
        >
          {(props.last_month_count >= 0 ? '+ ' : '') + props.last_month_count}
        </span>
      }
    </Grid>
  );
};

const StatsSection = () => {
  const [data, setData] = useState({
    user_count: 0,
    last_month_user_count: 0,
    video_count: 0,
    last_month_video_count: 0,
    comparison_count: 0,
    last_month_comparison_count: 0,
  });

  const matches = useMediaQuery('(min-width:600px)');

  const updateState = (value: Statistics) => {
    setData({
      user_count: value.user_count,
      video_count: value.video_count,
      comparison_count: value.comparison_count,
      last_month_user_count: value.last_month_user_count,
      last_month_video_count: value.last_month_video_count,
      last_month_comparison_count: value.last_month_video_count,
    });
  };

  useEffect(() => {
    StatsService.statsRetrieve()
      .then(updateState)
      .catch((error) => {
        console.log(error);
      });
  }, []);

  return (
    <Grid
      container
      style={{ background: 'black', color: 'white', textAlign: 'center' }}
      direction={!matches ? 'column' : 'row'}
    >
      <StatsUi
        text="User Count"
        count={data.user_count}
        last_month_count={data.last_month_user_count}
      />
      <StatsUi
        text="Comparison Count"
        count={data.comparison_count}
        last_month_count={data.last_month_comparison_count}
      />
      <StatsUi
        text="Video Count"
        count={data.video_count}
        last_month_count={data.last_month_video_count}
      />
    </Grid>
  );
};

export default StatsSection;
