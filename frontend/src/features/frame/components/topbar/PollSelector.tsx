import React from 'react';
import { Link } from 'react-router-dom';
import { Grid, Hidden, Typography } from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

const PollSelector = () => {
  const { name: pollName } = useCurrentPoll();

  return (
    <Link to="/">
      <Hidden smDown>
        <Grid container alignItems="center" spacing={1}>
          <Grid item>
            <img src="/svg/LogoSmall.svg" alt="logo" />
          </Grid>
          <Grid item>
            <Typography variant="h3" sx={{ fontSize: '1.4em !important' }}>
              Tournesol
            </Typography>
            <Typography variant="subtitle1">{pollName}</Typography>
          </Grid>
        </Grid>
      </Hidden>
      <Hidden smUp>
        <img src="/svg/LogoSmall.svg" alt="logo" />
      </Hidden>
    </Link>
  );
};

export default PollSelector;
