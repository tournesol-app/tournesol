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

import { selectFrame } from '../../drawerOpenSlice';
import { topBarHeight } from '../topbar/TopBar';
import {
  Compare as CompareIcon,
  EmojiEvents as EmojiEventsIcon,
  Home as HomeIcon,
  Info as InfoIcon,
  ListAlt as ListIcon,
  Stars as StarsIcon,
  TableRows as TableRowsIcon,
  VideoLibrary,
  WatchLater as WatchLaterIcon,
} from '@mui/icons-material';

import { closeDrawer } from '../../drawerOpenSlice';
import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { LanguageSelector } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  getRecommendationPageName,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { RouteID } from 'src/utils/types';
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
    '&:first-letter': {
      textTransform: 'capitalize',
    },
  },
}));

const SideBar = () => {
  const classes = useStyles();
  const theme = useTheme();

  const { t } = useTranslation();
  const location = useLocation();
  const dispatch = useAppDispatch();

  const { name: pollName, options } = useCurrentPoll();
  const path = options && options.path ? options.path : '/';
  const disabledItems = options?.disabledRouteIds ?? [];
  const defaultRecoSearchParams = options?.defaultRecoSearchParams
    ? '?' + options?.defaultRecoSearchParams
    : '';

  const drawerOpen = useAppSelector(selectFrame);
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));

  // parameter 'url', which corresponds to the target url, may contain some url parameters
  // we make sure that we highlight the component the user loaded
  const isItemSelected = (url: string) =>
    url.split('?')[0] === location.pathname;

  const menuItems = [
    {
      id: RouteID.Home,
      targetUrl: path,
      IconComponent: HomeIcon,
      displayText: t('menu.home'),
    },
    {
      id: RouteID.CollectiveRecommendations,
      targetUrl: `${path}recommendations${defaultRecoSearchParams}`,
      IconComponent:
        pollName === YOUTUBE_POLL_NAME ? VideoLibrary : TableRowsIcon,
      displayText: getRecommendationPageName(t, pollName),
    },
    { displayText: 'divider_1' },
    {
      id: RouteID.Comparison,
      targetUrl: `${path}comparison`,
      IconComponent: CompareIcon,
      displayText: t('menu.compare'),
    },
    {
      id: RouteID.MyComparisons,
      targetUrl: `${path}comparisons`,
      IconComponent: ListIcon,
      displayText: t('menu.myComparisons'),
    },
    {
      id: RouteID.MyComparedItems,
      targetUrl: `${path}ratings`,
      IconComponent: StarsIcon,
      displayText: t('menu.comparedItems'),
    },
    {
      id: RouteID.MyRateLaterList,
      targetUrl: `${path}rate_later`,
      IconComponent: WatchLaterIcon,
      displayText: t('menu.myRateLaterList'),
    },
    {
      id: RouteID.MyFeedback,
      targetUrl: `${path}personal/feedback`,
      IconComponent: EmojiEventsIcon,
      displayText: t('menu.myResults'),
    },
    { displayText: 'divider_2' },
    {
      id: RouteID.About,
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
        {menuItems.map(({ id, targetUrl, IconComponent, displayText }) => {
          if (!IconComponent || !targetUrl)
            return <Divider key={displayText} />;
          if (id && disabledItems.includes(id)) {
            return;
          }

          const selected = isItemSelected(targetUrl);
          return (
            <ListItem
              key={id}
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
