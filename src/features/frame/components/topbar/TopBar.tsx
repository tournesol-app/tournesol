import React from 'react';
import { Link, useHistory } from 'react-router-dom';

import { makeStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Grid from '@material-ui/core/Grid';
import Hidden from '@material-ui/core/Hidden';
import IconButton from '@material-ui/core/IconButton';
import Toolbar from '@material-ui/core/Toolbar';

import { Menu } from '@material-ui/icons';

import { useAppSelector, useAppDispatch } from '../../../../app/hooks';
import { openDrawer, closeDrawer, selectFrame } from '../../drawerOpenSlice';
import AccountInfo from './AccountInfo';

export const topBarHeight = 80;

const useStyles = makeStyles((theme) => ({
  appBar: { zIndex: theme.zIndex.drawer + 1 },
  container: {
    width: '100%',
  },
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: topBarHeight,
    padding: 4,
  },
  logo: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
  },
  search: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  searchTerm: {
    border: '1px solid #F1EFE7',
    borderRight: 'none',
    padding: '5px',
    height: '36px',
    borderRadius: '4px 0px 0px 4px',
    boxSizing: 'border-box',
    outline: 'none',
    color: '#9dbfaf',
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 400,
    fontSize: '18px',
    lineHeight: '28px',
    width: 472,
    maxWidth: 'calc(100% - 76px)',
  },
  searchButton: {
    width: '76px',
    height: '36px',
    border: '1px solid #F1EFE7',
    background: '#F1EFE7',
    color: '#fff',
    cursor: 'pointer',
    borderRadius: '0px 4px 4px 0px',
  },
}));

const Logo = () => {
  const classes = useStyles();
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();

  return (
    <Grid item md={4} xs={4} className={classes.logo}>
      <IconButton
        onClick={() => dispatch(drawerOpen ? closeDrawer() : openDrawer())}
      >
        <Menu />
      </IconButton>
      <Link to="/home">
        <Hidden xsDown>
          <img src="/svg/Logo.svg" alt="logo" />
        </Hidden>
        <Hidden smUp>
          <img src="/svg/LogoSmall.svg" alt="logo" />
        </Hidden>
      </Link>
    </Grid>
  );
};

const Search = () => {
  const classes = useStyles();
  const history = useHistory();
  const onSubmit = (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formElements = form.elements as typeof form.elements & {
      searchInput: HTMLInputElement;
    };
    history.push('/recommendations/?search=' + formElements.searchInput.value);
  };

  return (
    <Grid item md={4}>
      <form onSubmit={onSubmit} className={classes.search}>
        <input
          type="text"
          className={classes.searchTerm}
          id="searchInput"
        ></input>
        <button type="submit" className={classes.searchButton}>
          <img src="/svg/Search.svg" alt="search" />
        </button>
      </form>
    </Grid>
  );
};

const TopBar = () => {
  const classes = useStyles();
  return (
    <AppBar position="sticky" className={classes.appBar}>
      <Toolbar className={classes.toolbar}>
        <Grid container className={classes.container}>
          <Logo />
          <Hidden smDown>
            <Search />
          </Hidden>
          <AccountInfo />
        </Grid>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
