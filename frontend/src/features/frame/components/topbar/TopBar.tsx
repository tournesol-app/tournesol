import React from 'react';

import AppBar from '@mui/material/AppBar';
import Grid from '@mui/material/Grid';
import Toolbar from '@mui/material/Toolbar';
import useMediaQuery from '@mui/material/useMediaQuery';

import { useTheme } from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

import TopBarDesktop from './TopBarDesktop';
import TopBarMobile from './TopBarMobile';
import PwaBanner from './PwaBanner';
import { BeforeInstallPromptEvent } from '../../pwaPrompt';

// Allow to position contents like the footer relatively to the top of the
// page.
export const topBarHeight = 62;

interface Props {
  beforeInstallPromptEvent?: BeforeInstallPromptEvent;
}

const TopBar = ({ beforeInstallPromptEvent }: Props) => {
  const theme = useTheme();
  const { options } = useCurrentPoll();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

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
        variant="dense"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: topBarHeight,
          padding: '0 8px !important',
        }}
      >
        <Grid container sx={{ width: '100%' }} alignItems="center">
          {isSmallScreen ? <TopBarMobile /> : <TopBarDesktop />}
        </Grid>
      </Toolbar>
      {isSmallScreen && (
        <PwaBanner beforeInstallPromptEvent={beforeInstallPromptEvent} />
      )}
    </AppBar>
  );
};

export default TopBar;
