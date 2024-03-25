import React from 'react';
import clsx from 'clsx';
import { useSelector } from 'react-redux';
import { useLocation, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Drawer,
  List,
  Theme,
  Divider,
  Tooltip,
  Avatar,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import makeStyles from '@mui/styles/makeStyles';
import useMediaQuery from '@mui/material/useMediaQuery';

import { selectFrame } from '../../drawerOpenSlice';
import { topBarHeight } from '../topbar/TopBar';
import {
  Compare as CompareIcon,
  EmojiEvents as EmojiEventsIcon,
  Help as HelpIcon,
  Home as HomeIcon,
  Info as InfoIcon,
  ListAlt as ListIcon,
  Stars as StarsIcon,
  TableRows as TableRowsIcon,
  VideoLibrary,
  WatchLater as WatchLaterIcon,
} from '@mui/icons-material';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { LanguageSelector } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import {
  getRecommendationPageName,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { RouteID } from 'src/utils/types';
import { getDefaultRecommendationsSearchParams } from 'src/utils/userSettings';

import { closeDrawer } from '../../drawerOpenSlice';
import { BeforeInstallPromptEvent } from '../../pwaPrompt';

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
  listItemIconSelected: {
    color: theme.palette.neutral.dark,
  },
}));

interface Props {
  beforeInstallPromptEvent?: BeforeInstallPromptEvent;
}

const SideBar = ({ beforeInstallPromptEvent }: Props) => {
  const classes = useStyles();
  const theme = useTheme();

  const { t } = useTranslation();
  const location = useLocation();
  const dispatch = useAppDispatch();

  const userSettings = useSelector(selectSettings)?.settings;
  const { name: pollName, options } = useCurrentPoll();
  const path = options && options.path ? options.path : '/';
  const disabledItems = options?.disabledRouteIds ?? [];

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
      ariaLabel: t('menu.homeAriaLabel'),
    },
    {
      id: RouteID.CollectiveRecommendations,
      targetUrl: `${path}recommendations${getDefaultRecommendationsSearchParams(
        pollName,
        options,
        userSettings
      )}`,
      IconComponent:
        pollName === YOUTUBE_POLL_NAME ? VideoLibrary : TableRowsIcon,
      displayText: getRecommendationPageName(t, pollName),
      ariaLabel: t('menu.recommendationsAriaLabel'),
    },
    { displayText: 'divider_1' },
    {
      id: RouteID.Comparison,
      targetUrl: `${path}comparison`,
      IconComponent: CompareIcon,
      displayText: t('menu.compare'),
      ariaLabel: t('menu.compareAriaLabel'),
    },
    {
      id: RouteID.MyComparisons,
      targetUrl: `${path}comparisons`,
      IconComponent: ListIcon,
      displayText: t('menu.myComparisons'),
      ariaLabel: t('menu.myComparisonsAriaLabel'),
    },
    {
      id: RouteID.MyComparedItems,
      targetUrl: `${path}ratings`,
      IconComponent: StarsIcon,
      displayText: t('menu.comparedItems'),
      ariaLabel: t('menu.myComparedItemsAriaLabel'),
    },
    {
      id: RouteID.MyRateLaterList,
      targetUrl: `${path}rate_later`,
      IconComponent: WatchLaterIcon,
      displayText: t('menu.myRateLaterList'),
      ariaLabel: t('menu.myRateLaterListAriaLabel'),
    },
    {
      id: RouteID.MyFeedback,
      targetUrl: `${path}personal/feedback`,
      IconComponent: EmojiEventsIcon,
      displayText: t('menu.myResults'),
      ariaLabel: t('menu.myFeedbackAriaLabel'),
    },
    { displayText: 'divider_2' },
    {
      id: RouteID.FAQ,
      targetUrl: '/faq',
      IconComponent: HelpIcon,
      displayText: t('menu.faq'),
      ariaLabel: t('menu.FAQAriaLabel'),
    },
    {
      id: RouteID.About,
      targetUrl: '/about',
      IconComponent: InfoIcon,
      displayText: t('menu.about'),
      ariaLabel: t('menu.aboutAriaLabel'),
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
        sx={{
          flexGrow: 1,
          wordBreak: 'break-word',
          '& > .MuiListItemButton-root': {
            minHeight: '56px',
          },
          '& .MuiListItemIcon-root': {
            color: theme.palette.grey[400],
            minWidth: '40px',
          },
          '& .MuiListItemText-primary': {
            fontWeight: 'bold',
            '&:first-letter': {
              textTransform: 'capitalize',
            },
          },
        }}
      >
        {menuItems.map(
          ({ id, targetUrl, IconComponent, displayText, ariaLabel }) => {
            if (!IconComponent || !targetUrl)
              return <Divider key={displayText} />;
            if (id && disabledItems.includes(id)) {
              return;
            }

            const selected = isItemSelected(targetUrl);
            return (
              <ListItemButton
                key={id}
                aria-label={ariaLabel}
                selected={selected}
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
                  <ListItemIcon>
                    <IconComponent
                      className={clsx({
                        [classes.listItemIconSelected]: selected,
                      })}
                    />
                  </ListItemIcon>
                </Tooltip>
                <ListItemText primary={displayText} />
              </ListItemButton>
            );
          }
        )}
        {beforeInstallPromptEvent && (
          <>
            <Divider />
            <ListItemButton onClick={() => beforeInstallPromptEvent.prompt()}>
              <ListItemIcon>
                <Avatar
                  src="/icons/maskable-icon-512x512.png"
                  sx={{ width: '24px', height: '24px' }}
                />
              </ListItemIcon>
              <ListItemText
                primary={t('menu.installTheApp')}
                primaryTypographyProps={{ color: theme.palette.neutral.dark }}
              />
            </ListItemButton>
          </>
        )}
      </List>
      <Divider />
      <LanguageSelector languageName={drawerOpen} />
    </Drawer>
  );
};

export default SideBar;
