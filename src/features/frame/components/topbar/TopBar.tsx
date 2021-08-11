import React from 'react';
import { Link } from 'react-router-dom';

import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import { Menu } from '@material-ui/icons';

import { useAppSelector, useAppDispatch } from '../../../../app/hooks';
import { openDrawer, closeDrawer, selectFrame } from '../../drawerOpenSlice';

export const topBarHeight = 80;

const useStyles = makeStyles((theme) => ({
  appBar: { zIndex: theme.zIndex.drawer + 1 },
  grow: {
    flexGrow: 1,
  },
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: topBarHeight,
    padding: 4,
  },
  sectionDesktop: {
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'flex',
    },
  },
  search: {
    position: 'absolute',
  },

  searchTerm: {
    width: '484px',
    border: '1px solid #F1EFE7',
    borderRight: 'none',
    padding: '5px',
    height: '36px',
    borderRadius: '4px',
    boxSizing: 'border-box',
    outline: 'none',
    color: '#9dbfaf',
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 400,
    fontSize: '18px',
    lineHeight: '28px',
  },

  searchButton: {
    width: '76px',
    right: '0px',
    top: '0px',
    bottom: '0px',
    height: '36px',
    border: '1px solid #F1EFE7',
    background: '#F1EFE7',
    color: '#fff',
    cursor: 'pointer',
    position: 'absolute',
    'border-radius': '0px 4px 4px 0px',
  },

  LogInButton: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    padding: '11px 16px',

    position: 'static',

    /* Primary/Sunflower/A-30 */

    border: '2px solid #806300',
    boxSizing: 'border-box',
    borderRadius: '4px',
    background: '#FFC800',

    /* Inside Auto Layout */

    flex: 'none',
    order: 1,
    flexGrow: 0,
    marginRight: '16px',

    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    fontSize: '16px',
    lineHeight: '18px',
    color: '#806300',
  },

  JoinUsButton: {
    /* Auto Layout */

    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    padding: '11px 16px',

    position: 'static',

    border: '2px solid #3198C4',
    boxSizing: 'border-box',
    background: '#3198C4',
    borderRadius: '4px',

    /* Inside Auto Layout */

    flex: 'none',
    order: 1,
    flexGrow: 0,
    marginRight: '0px',

    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    fontSize: '16px',
    lineHeight: '18px',
    color: '#FFFFFF',
  },
}));

const TopBar = () => {
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();
  return (
    <AppBar position="sticky" className={classes.appBar}>
      <Toolbar className={classes.toolbar}>
        <IconButton
          onClick={() => dispatch(drawerOpen ? closeDrawer() : openDrawer())}
        >
          <Menu />
        </IconButton>
        <Link to="/home">
          <img src="svg/Logo.svg" alt="logo" />
        </Link>
        <div className={classes.search}>
          <input
            type="text"
            className={classes.searchTerm}
            id="input_text"
          ></input>
          <button type="submit" className={classes.searchButton}>
            <img src="svg/Search.svg" alt="search" />
          </button>
        </div>

        <div className={classes.grow} />
        <div className={classes.sectionDesktop}>
          <Link className={classes.LogInButton} to="/login">
            Log in
          </Link>
          <Link className={classes.JoinUsButton} to="/signup">
            Join us
          </Link>
        </div>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
