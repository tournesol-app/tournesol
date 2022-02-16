import React from 'react';
import clsx from 'clsx';
import { useLocation, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ListItem,
  ListItemText,
  ListItemIcon,
  Drawer,
  List,
  Theme,
  Divider,
  Tooltip,
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
import { LanguageSelector } from 'src/components';

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
    backgroundColor: theme.palette.background.menu,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    overflowX: 'hidden',
    [theme.breakpoints.down('md')]: {
      top: 0,
      height: '100%',
    },
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
    color: theme.palette.neutral.dark,
  },
  listItemText: {
    fontWeight: 'bold',
  },
}));

const SideBar = () => {
  const { t } = useTranslation();
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();

  const isItemSelected = (url: string) => url === location.pathname;

  const menuItems = [
    { targetUrl: '/', IconComponent: HomeIcon, displayText: t('menu.home') },
    {
      targetUrl: '/recommendations?date=Month',
      IconComponent: VideoLibrary,
      displayText: t('menu.recommendations'),
    },
    { displayText: 'divider_1' },
    {
      targetUrl: '/comparison',
      IconComponent: CompareIcon,
      displayText: t('menu.compare'),
    },
    {
      targetUrl: '/comparisons',
      IconComponent: ListIcon,
      displayText: t('menu.myComparisons'),
    },
    {
      targetUrl: '/ratings',
      IconComponent: StarsIcon,
      displayText: t('menu.myRatedVideos'),
    },
    {
      targetUrl: '/rate_later',
      IconComponent: WatchLaterIcon,
      displayText: t('menu.myRateLaterList'),
    },
    { displayText: 'divider_2' },
    {
      targetUrl: '/about',
      IconComponent: InfoIcon,
      displayText: t('menu.about'),
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
        sx={{ flexGrow: 1 }}
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
              sx={{
                '&.Mui-selected': {
                  bgcolor: 'action.selected',
                },
                '&.Mui-selected:hover': {
                  bgcolor: 'action.selected',
                },
              }}
            >
              <Tooltip
                title={drawerOpen === true ? '' : displayText}
                placement="right"
                arrow
              >
                <ListItemIcon sx={{ minWidth: '40px' }}>
                  <IconComponent
                    className={clsx({
                      [classes.listItemIcon]: !selected,
                      [classes.listItemIconSelected]: selected,
                    })}
                  />
                </ListItemIcon>
              </Tooltip>
              <ListItemText
                primary={displayText}
                primaryTypographyProps={{ className: classes.listItemText }}
              />
            </ListItem>
          );
        })}
      </List>
      {drawerOpen && <Footer />}
      <LanguageSelector languageName={drawerOpen} />
    </Drawer>
  );
};

export default SideBar;
