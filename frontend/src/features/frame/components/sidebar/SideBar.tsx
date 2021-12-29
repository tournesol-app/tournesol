import React from 'react';
import clsx from 'clsx';
import { useLocation, Link } from 'react-router-dom';
import {
  ListItem,
  ListItemText,
  ListItemIcon,
  Drawer,
  List,
  Theme,
  Divider,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import makeStyles from '@mui/styles/makeStyles';
import useMediaQuery from '@mui/material/useMediaQuery';

import { useAppSelector } from '../../../../app/hooks';
import { selectFrame } from '../../drawerOpenSlice';
import { topBarHeight } from '../topbar/TopBar';
import {
  Home as HomeIcon,
  Compare as CompareIcon,
  WatchLater as WatchLaterIcon,
  ListAlt as ListIcon,
  Info as InfoIcon,
  Stars as StarsIcon,
  VideoLibrary,
} from '@mui/icons-material';

import { useAppDispatch } from '../../../../app/hooks';
import { closeDrawer } from '../../drawerOpenSlice';
import Footer from './Footer';

export const sideBarWidth = 264;

const useStyles = makeStyles((theme: Theme) => ({
  drawer: {
    width: sideBarWidth,
    flexShrink: 0,
    minHeight: '100%',
    position: 'relative',
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
    width: `calc(${theme.spacing(7)} + 1px)`,
  },
  drawerPaper: {
    top: topBarHeight,
    height: `calc(100% - ${topBarHeight}px)`,
    backgroundColor: '#FAF8F3',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    [theme.breakpoints.down('md')]: {
      top: 0,
      height: '100%',
    },
    overflowX: 'hidden',
    '& > *': {
      // All direct children of the drawer paper should keep a min-width:
      // their content should not be wrapped during the drawer animation.
      minWidth: `${sideBarWidth}px`,
    },
  },
  listItem: {
    height: '64px',
  },
  listItemIcon: {
    color: '#CDCABC',
  },
  listItemIconSelected: {
    color: '#806300',
  },
  listItemText: {
    fontWeight: 'bold',
  },
}));

const SideBar = () => {
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();

  const isItemSelected = (url: string) => url === location.pathname;

  const menuItems = [
    { targetUrl: '/', IconComponent: HomeIcon, displayText: 'Home' },
    {
      targetUrl: '/recommendations',
      IconComponent: VideoLibrary,
      displayText: 'Recommendations',
    },
    { displayText: 'divider_1' },
    {
      targetUrl: '/comparison',
      IconComponent: CompareIcon,
      displayText: 'Contribute',
    },
    {
      targetUrl: '/comparisons',
      IconComponent: ListIcon,
      displayText: 'My comparisons',
    },
    {
      targetUrl: '/ratings',
      IconComponent: StarsIcon,
      displayText: 'My rated videos',
    },
    {
      targetUrl: '/rate_later',
      IconComponent: WatchLaterIcon,
      displayText: 'My rate later list',
    },
    { displayText: 'divider_2' },
    {
      targetUrl: '/about',
      IconComponent: InfoIcon,
      displayText: 'About',
    },
  ];

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
      <List
        disablePadding
        onClick={isSmallScreen ? () => dispatch(closeDrawer()) : undefined}
      >
        {menuItems.map(({ targetUrl, IconComponent, displayText }) => {
          if (!IconComponent || !targetUrl)
            return <Divider key={displayText} />;
          const selected = isItemSelected(targetUrl);
          return (
            <ListItem
              key={displayText}
              button
              selected={selected}
              className={classes.listItem}
              component={Link}
              to={targetUrl}
            >
              <ListItemIcon>
                <IconComponent
                  className={clsx({
                    [classes.listItemIcon]: !selected,
                    [classes.listItemIconSelected]: selected,
                  })}
                />
              </ListItemIcon>
              <ListItemText
                primary={displayText}
                primaryTypographyProps={{ className: classes.listItemText }}
              />
            </ListItem>
          );
        })}
      </List>
      {drawerOpen && <Footer />}
    </Drawer>
  );
};

export default SideBar;
