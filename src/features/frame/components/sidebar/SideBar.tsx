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
import { makeStyles } from '@material-ui/core/styles';
import { Search } from '@material-ui/icons';

import { useAppSelector } from '../../../../app/hooks';
import { selectFrame } from '../../drawerOpenSlice';
import { topBarHeight } from '../topbar/TopBar';

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
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(7) + 1,
    },
  },
  drawerPaper: {
    top: topBarHeight,
  },
}));

const SideBar = () => {
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  return (
    <Drawer
      variant="permanent"
      anchor="left"
      open={true}
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
      <List>
        <Link to="/">
          <ListItem button>
            <ListItemIcon>
              <Search color="primary" />
            </ListItemIcon>
            <ListItemText primary="Home" />
          </ListItem>
        </Link>
        <Link to="/login">
          <ListItem button>
            <ListItemIcon>
              <Search color="primary" />
            </ListItemIcon>
            <ListItemText primary="Login" />
          </ListItem>
        </Link>
        <Link to="/comparisons">
          <ListItem button>
            <ListItemIcon>
              <Search color="primary" />
            </ListItemIcon>
            <ListItemText primary="Comparisons" />
          </ListItem>
        </Link>
      </List>
    </Drawer>
  );
};

export default SideBar;
