import React from 'react';

import AppBar from '@mui/material/AppBar';
import Grid from '@mui/material/Grid';
import Hidden from '@mui/material/Hidden';
import Toolbar from '@mui/material/Toolbar';

import { useTheme } from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

import LargeScreenTopBar from './LargeScreenTopBar';
import MobileTopBar from './MobileTopBar';

// Allow to position contents like the footer relatively to the top of the
// page.
export const topBarHeight = 80;

const TopBar = () => {
  const theme = useTheme();
  const { options } = useCurrentPoll();

  return (
    <AppBar
      position="sticky"
      sx={{
        background: options?.topBarBackground
          ? options.topBarBackground
          : undefined,
        [theme.breakpoints.up('md')]: { zIndex: theme.zIndex.drawer + 1 },
      }}
    >
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: topBarHeight,
          padding: '4px !important',
        }}
      >
        <Grid container sx={{ width: '100%' }}>
          <Hidden mdDown>
            <LargeScreenTopBar />
          </Hidden>
          <Hidden mdUp>
            <MobileTopBar />
          </Hidden>
        </Grid>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
