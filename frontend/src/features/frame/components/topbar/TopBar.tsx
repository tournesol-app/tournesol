import React, { useState } from 'react';
import { Link, useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import AppBar from '@mui/material/AppBar';
import Grid from '@mui/material/Grid';
import Hidden from '@mui/material/Hidden';
import IconButton from '@mui/material/IconButton';
import Toolbar from '@mui/material/Toolbar';

import { Menu } from '@mui/icons-material';

import { useAppSelector, useAppDispatch } from '../../../../app/hooks';
import { openDrawer, closeDrawer, selectFrame } from '../../drawerOpenSlice';
import AccountInfo from './AccountInfo';

export const topBarHeight = 80;

const useStyles = makeStyles((theme) => ({
  appBar: { [theme.breakpoints.up('md')]: { zIndex: theme.zIndex.drawer + 1 } },
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
    height: '100%',
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
        size="large"
      >
        <Menu />
      </IconButton>
      <Link to="/">
        <Hidden smDown>
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
  const { t } = useTranslation();
  const classes = useStyles();
  const history = useHistory();
  const paramsString = useLocation().search;
  const searchParams = new URLSearchParams(paramsString);
  const [search, setSearch] = useState(searchParams.get('search') || '');

  const onSubmit = (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    searchParams.delete('search');
    searchParams.append('search', search);
    searchParams.delete('offset');
    history.push('/recommendations/?' + searchParams.toString());
  };

  return (
    <Grid item md={4}>
      <form onSubmit={onSubmit} className={classes.search}>
        <input
          type="text"
          className={classes.searchTerm}
          id="searchInput"
          defaultValue={search}
          onChange={(e) => setSearch(e.target.value)}
        ></input>
        <button type="submit" className={classes.searchButton}>
          <img src="/svg/Search.svg" alt={t('topbar.search')} />
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
          <Hidden mdDown>
            <Search />
          </Hidden>
          <AccountInfo />
        </Grid>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
