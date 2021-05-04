import React from 'react';
import clsx from 'clsx';

import { makeStyles, useTheme } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Alert from '@material-ui/lab/Alert';
import WbSunny from '@material-ui/icons/WbSunny';
import FunctionsIcon from '@material-ui/icons/Functions';
import PersonIcon from '@material-ui/icons/Person';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ExitToAppIcon from '@material-ui/icons/ExitToApp';
import SupervisorAccountIcon from '@material-ui/icons/SupervisorAccount';
import StorageIcon from '@material-ui/icons/Storage';
import AssessmentIcon from '@material-ui/icons/Assessment';
import SearchIcon from '@material-ui/icons/Search';
import YouTubeIcon from '@material-ui/icons/YouTube';
import ListAltIcon from '@material-ui/icons/ListAlt';
import BugReportIcon from '@material-ui/icons/BugReport';
import MenuBookIcon from '@material-ui/icons/MenuBook';
import MoreHorizIcon from '@material-ui/icons/MoreHoriz';
import QueuePlayNextIcon from '@material-ui/icons/QueuePlayNext';

import { library } from '@fortawesome/fontawesome-svg-core';
import { fab } from '@fortawesome/free-brands-svg-icons';
import { fas, faUserSecret, faDownload } from '@fortawesome/free-solid-svg-icons';

import { useHistory } from 'react-router-dom';

import { ExpandLess, ExpandMore } from '@material-ui/icons';
import Collapse from '@material-ui/core/Collapse';
import Tooltip from '@material-ui/core/Tooltip';
import Cookies from 'universal-cookie';
import Router from './Router';

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
  root: {
    position: 'absolute',
    display: 'flex',
    width: '100%',
    height: '100%',
    overflow: 'hidden',
  },
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
      width: theme.spacing(9) + 1,
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
  content: {
    flexGrow: 1,
    marginTop: '64px',
    height: 'calc(100% - 64px)',
    padding: '16px',
    paddingBottom: '0px',
    overflow: 'auto',
  },
  nested: {
    paddingLeft: theme.spacing(4),
  },
}));

const App = () => {
  const classes = useStyles();
  const cookies = new Cookies();

  const getCookieWithDefault = (key, defaultValue) => {
    const val = cookies.get(key);
    if (val === undefined) {
      return defaultValue;
    }

    return val;
  };

  const theme = useTheme();
  const history = useHistory();
  const [open, setOpen] = React.useState(
    getCookieWithDefault('menuOpen', 'true') === 'true',
  );

  const [moreOpen, setMoreOpen] = React.useState(
    getCookieWithDefault('menuMoreOpen', 'false') === 'true',
  );

  const handleMoreClick = () => {
    setMoreOpen(!moreOpen);
    cookies.set('menuMoreOpen', !moreOpen ? 'true' : 'false',
      { path: '/' });
  };

  const handleDrawerOpen = () => {
    setOpen(true);
    cookies.set('menuOpen', 'true', { path: '/' });
  };

  const handleDrawerClose = () => {
    setOpen(false);
    cookies.set('menuOpen', 'false', { path: '/' });
  };

  const nestedClass = open ? classes.nested : '';

  return (
    <div className={classes.root} id="id_menu_all">
      {/* For selenium to know the status of the menu faster */}
      {moreOpen ? <span id="id_more_open" />
        : <span id="id_more_closed" />}
      <CssBaseline />
      <AppBar
        position="fixed"
        className={clsx(classes.appBar, {
          [classes.appBarShift]: open,
        })}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            className={clsx(classes.menuButton, {
              [classes.hide]: open,
            })}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap>
            Tournesol
          </Typography>
          <WbSunny />

          {window.location.href.includes('staging.tournesol.app') && (
          <Alert
            severity="warning"
            icon
            variant="outlined"
            style={{ width: '70%', marginTop: '5px', marginBottom: '5px' }}
          >
            This is the staging platform of Tournesol.
            To access the actual Tournesol page, please go to{' '}
            <a href="https://tournesol.app">tournesol.app</a>.
            Please also{' '}
            <a href="mailto:tournesol.application@gmail.com">let us know</a>
            {' '}how you ended up on the staging platform, if it was by mistake.

          </Alert>
          )}

          {window.location.href.includes('127.0.0.1') && (
          <Alert
            severity="warning"
            icon
            variant="outlined"
            style={{ width: '70%', marginTop: '5px', marginBottom: '5px' }}
          >
            Development version

          </Alert>
          )}
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        className={clsx(classes.drawer, {
          [classes.drawerOpen]: open,
          [classes.drawerClose]: !open,
        })}
        classes={{
          paper: clsx({
            [classes.drawerOpen]: open,
            [classes.drawerClose]: !open,
          }),
        }}
      >
        <div className={classes.toolbar}>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === 'rtl' ? (
              <ChevronRightIcon />
            ) : (
              <ChevronLeftIcon />
            )}
          </IconButton>
        </div>
        <Divider />
        <List>
          <ListItem button onClick={() => history.push('/home')}>
            <ListItemIcon>
              <WbSunny />
            </ListItemIcon>
            <ListItemText primary="Home" />
          </ListItem>

          <Divider />

          <ListItem
            id="user_interface"
            button
            onClick={() => history.push('/recommendations')}
          >
            <ListItemIcon>
              <SearchIcon color="primary" />
            </ListItemIcon>
            <ListItemText primary="Search" />
          </ListItem>

          {window.is_authenticated ? (
            <ListItem button onClick={() => history.push('/rate_later')} id="rate_later_menu">
              <ListItemIcon>
                <QueuePlayNextIcon color="secondary" />
              </ListItemIcon>
              <ListItemText primary="Add videos" />
            </ListItem>
          ) : ''}

          {window.is_authenticated ? (
            <ListItem
              id="expert_interface"
              button
              onClick={() => history.push('/rate')}
            >
              <ListItemIcon>
                <FunctionsIcon color="secondary" />
              </ListItemIcon>
              <ListItemText primary="Rate videos" />
            </ListItem>
          ) : ''}

          {window.is_authenticated ? (
            <ListItem button onClick={() => history.push(`/user/${window.username}`)} id="personal_info_menu">
              <ListItemIcon>
                <PersonIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary="My profile" />
            </ListItem>
          ) : ''}

          <ListItem
            button
            id="more_button"
            component="a"
            onClick={() => handleMoreClick()}
          >
            <ListItemIcon>
              <MoreHorizIcon />
            </ListItemIcon>
            <ListItemText primary="More" />
            {moreOpen ? <ExpandLess /> : <ExpandMore />}
          </ListItem>

          <Collapse in={moreOpen} timeout="auto" unmountOnExit>
            <List component="div" disablePadding id="id_list_more">

              <ListItem
                className={nestedClass}
                id="tournesol_wiki"
                button
                component="a"
                href="https://wiki.tournesol.app"
              >
                <ListItemIcon>
                  <MenuBookIcon color="primary" />
                </ListItemIcon>
                <ListItemText primary="Tournesol Wiki" />
              </ListItem>

              {window.is_authenticated ? (
                <ListItem
                  button
                  onClick={() => history.push('/details')}
                  id="video_details_menu"
                  className={nestedClass}
                >
                  <ListItemIcon>
                    <YouTubeIcon />
                  </ListItemIcon>
                  <ListItemText primary="Videos" />
                </ListItem>
              ) : ''}

              {window.is_authenticated ? (
                <ListItem
                  button
                  onClick={() => history.push('/representative')}
                  id="representative_menu"
                  className={nestedClass}
                >
                  <ListItemIcon>
                    <ListAltIcon />
                  </ListItemIcon>
                  <ListItemText primary="Representative" />
                </ListItem>
              ) : ''}

              {window.is_authenticated ? (
                <ListItem
                  button
                  onClick={() => history.push('/inconsistencies')}
                  id="inconsistencies_menu"
                  className={nestedClass}
                >
                  <ListItemIcon>
                    <BugReportIcon />
                  </ListItemIcon>
                  <ListItemText primary="Inconsistencies" />
                </ListItem>
              ) : ''}
            </List>
          </Collapse>

          <Divider />

          {window.is_authenticated === 1 && (
            <ListItem
              button
              id="logout_button"
              component="a"
              onClick={() => history.push('/logout')}
            >
              <ListItemIcon>
                <ExitToAppIcon />
              </ListItemIcon>
              <Tooltip title={`You are ${window.username}`} aria-label="report">
                <ListItemText primary="Log out" />
              </Tooltip>
            </ListItem>
          )}

          {window.is_superuser ? (
            <div>
              <Divider />
              <ListItem button component="a" href="/admin/">
                <ListItemIcon>
                  <SupervisorAccountIcon />
                </ListItemIcon>
                <ListItemText primary="Administration" />
              </ListItem>
              <ListItem button component="a" href="/api/v2/">
                <ListItemIcon>
                  <StorageIcon />
                </ListItemIcon>
                <ListItemText primary="API explorer" />
              </ListItem>
              <ListItem button component="a" href="/files/">
                <ListItemIcon>
                  <AssessmentIcon />
                </ListItemIcon>
                <ListItemText primary="Training artifacts" />
              </ListItem>
            </div>) : ''}

        </List>
      </Drawer>

      <main className={classes.content}>
        <Router />
      </main>
    </div>
  );
};

export default App;

// react initialzation
library.add(fab, faUserSecret);
library.add(fas, faDownload);
