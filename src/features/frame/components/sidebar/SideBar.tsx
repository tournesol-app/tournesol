import React from 'react';
import clsx from 'clsx';
import { IconButton, ListItem, ListItemText, ListItemIcon, Divider, Drawer, List } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Search, ChevronLeft } from '@material-ui/icons';
import { useAppSelector, useAppDispatch } from '../../../../app/hooks';
import {
  closeDrawer,
  selectFrame,
} from '../../drawerOpenSlice';

const drawerWidth = 240;

const useStyles = makeStyles((theme: any) => ({
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
  },
  drawerOpen: {
    width: drawerWidth,
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
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
  },
}));

const SideBar = (props: any) => {
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();
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
        paper: clsx({
          [classes.drawerOpen]: drawerOpen,
          [classes.drawerClose]: !drawerOpen,
        }),
      }}
    >
      <IconButton className={classes.toolbar} onClick={() => dispatch(closeDrawer())}>
        <ChevronLeft />
      </IconButton>
      <Divider />
      <List>
        <ListItem button>
          <ListItemIcon>
            <Search color="primary" />
          </ListItemIcon>
          <ListItemText primary="A" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <Search color="primary" />
          </ListItemIcon>
          <ListItemText primary="B" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <Search color="primary" />
          </ListItemIcon>
          <ListItemText primary="C" />
        </ListItem>
      </List>
    </Drawer>
  );
}

export default SideBar;
