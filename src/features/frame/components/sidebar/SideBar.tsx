import React from 'react';
import clsx from 'clsx';
import { Link } from 'react-router-dom';
import {
  ListItem,
  ListItemText,
  ListItemIcon,
  Drawer,
  List,
  Theme,
} from '@material-ui/core';
import { makeStyles, useTheme } from '@material-ui/core/styles';
import useMediaQuery from '@material-ui/core/useMediaQuery';

import { useAppSelector } from '../../../../app/hooks';
import { selectFrame } from '../../drawerOpenSlice';
import { topBarHeight } from '../topbar/TopBar';
import {
  Home as HomeIcon,
  Compare as CompareIcon,
  WatchLater as WatchLaterIcon,
  VideoLibrary,
} from '@material-ui/icons';

import { useAppDispatch } from '../../../../app/hooks';
import { closeDrawer } from '../../drawerOpenSlice';

export const sideBarWidth = 240;

const useStyles = makeStyles((theme: Theme) => ({
  drawer: {
    width: sideBarWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
  },
  drawerOpen: {
    width: sideBarWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerClose: {
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    overflowX: 'hidden',
    width: theme.spacing(7) + 1,
  },
  drawerPaper: {
    top: topBarHeight,
    [theme.breakpoints.down('sm')]: {
      top: 0,
    },
  },
}));

const SideBar = () => {
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Drawer
      variant={isSmallScreen ? 'temporary' : 'permanent'}
      anchor="left"
      open={drawerOpen}
      onClose={() => dispatch(closeDrawer())}
      className={clsx(classes.drawer, {
        [classes.drawerOpen]: drawerOpen,
        [classes.drawerClose]: !drawerOpen,
      })}
      classes={{
        paper: clsx(classes.drawerPaper, {
          [classes.drawerOpen]: drawerOpen,
          [classes.drawerClose]: !drawerOpen,
        }),
      }}
    >
      <List onClick={isSmallScreen ? () => dispatch(closeDrawer()) : undefined}>
        <Link to="/">
          <ListItem button>
            <ListItemIcon>
              <HomeIcon color="action" />
            </ListItemIcon>
            <ListItemText primary="Home" />
          </ListItem>
        </Link>
        <Link to="/comparisons">
          <ListItem button>
            <ListItemIcon>
              <CompareIcon color="action" />
            </ListItemIcon>
            <ListItemText primary="Comparisons" />
          </ListItem>
        </Link>
        <Link to="/rate_later">
          <ListItem button>
            <ListItemIcon>
              <WatchLaterIcon color="action" />
            </ListItemIcon>
            <ListItemText primary="Rate later" />
          </ListItem>
        </Link>
        <Link to="/recommendations">
          <ListItem button>
            <ListItemIcon>
              <VideoLibrary color="action" />
            </ListItemIcon>
            <ListItemText primary="Recommendations" />
          </ListItem>
        </Link>
      </List>
    </Drawer>
  );
};

export default SideBar;
