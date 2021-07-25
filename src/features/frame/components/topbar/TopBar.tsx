import React from 'react';
import clsx from 'clsx';
import {
  AppBar,
  Typography,
  IconButton,
  Toolbar,
  makeStyles,
} from '@material-ui/core';
import { Menu, WbSunny } from '@material-ui/icons';
import { useAppSelector, useAppDispatch } from '../../../../app/hooks';
import { openDrawer, selectFrame } from '../../drawerOpenSlice';

const drawerWidth = 240;

const useStyles = makeStyles((theme: any) => ({
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  hide: {
    display: 'none',
  },
}));

const TopBar = () => {
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();
  return (
    <AppBar
      className={clsx(classes.appBar, {
        [classes.appBarShift]: drawerOpen,
      })}
    >
      <Toolbar>
        {!drawerOpen && (
          <IconButton onClick={() => dispatch(openDrawer())}>
            <Menu />
          </IconButton>
        )}
        <Typography variant="h6" noWrap>
          Tournesol
        </Typography>
        <WbSunny />
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
