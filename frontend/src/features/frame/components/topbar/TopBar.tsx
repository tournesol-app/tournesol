import React, { useState } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
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
import { useTheme } from '@mui/material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { polls } from 'src/utils/constants';
import PollSelector from './PollSelector';

// Allow to position contents like the footer relatively to the top of the
// page.
export const topBarHeight = 80;

const useStyles = makeStyles(() => ({
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
  searchClose: {
    cursor: 'pointer',
    position: 'absolute',
    left: 'calc(50% - 5px)',
  },
  searchOpen: {
    cursor: 'pointer',
  },
}));

const Logo = () => {
  const drawerOpen = useAppSelector(selectFrame);
  const dispatch = useAppDispatch();

  return (
    <Grid
      item
      md={4}
      sm={2}
      xs={3}
      sx={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
      }}
    >
      <IconButton
        onClick={() => dispatch(drawerOpen ? closeDrawer() : openDrawer())}
        size="large"
      >
        <Menu />
      </IconButton>
      <PollSelector polls={polls} />
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
  );
};

const TopBar = () => {
  const theme = useTheme();
  const { options } = useCurrentPoll();

  const classes = useStyles();

  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  const searchOpeningHandler = (open: boolean) => {
    setMobileSearchOpen(open);
  };

  return (
    <AppBar
      position="sticky"
      sx={{
        background: options?.topBarBackground
          ? options.topBarBackground
          : undefined,
        [theme.breakpoints.up('md')]: { zIndex: theme.zIndex.drawer + 1 },
      }}
    >
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: topBarHeight,
          padding: '4px !important',
        }}
      >
        <Grid container sx={{ width: '100%', maxWidth: '100%' }}>
          <Hidden mdDown>
            <Logo />
            <Grid item md={4}>
              {options?.withSearchBar && <Search />}
            </Grid>
            <AccountInfo />
          </Hidden>
          <Hidden mdUp>
            {!mobileSearchOpen && <Logo />}
            {!mobileSearchOpen && (
              <Grid
                item
                xs={2}
                padding={2}
                onClick={() => searchOpeningHandler(true)}
              >
                <svg
                  width="27"
                  height="27"
                  viewBox="0 0 18 18"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className={classes.searchOpen}
                >
                  <path
                    d="M11 0C9.27609 0 7.62279 0.684819 6.40381 1.90381C5.18482 3.12279 4.5 4.77609 4.5 6.5C4.5 8.11 5.09 9.59 6.06 10.73L5.79 11H5L0 16L1.5 17.5L6.5 12.5V11.71L6.77 11.44C7.94945 12.4468 9.44929 12.9999 11 13C12.7239 13 14.3772 12.3152 15.5962 11.0962C16.8152 9.87721 17.5 8.22391 17.5 6.5C17.5 4.77609 16.8152 3.12279 15.5962 1.90381C14.3772 0.684819 12.7239 0 11 0ZM11 2C13.5 2 15.5 4 15.5 6.5C15.5 9 13.5 11 11 11C8.5 11 6.5 9 6.5 6.5C6.5 4 8.5 2 11 2Z"
                    fill="#1d1a14"
                  />
                </svg>
              </Grid>
            )}
            {mobileSearchOpen && (
              <Grid item md={12} width="100%">
                {options?.withSearchBar && <Search />}
                <span
                  title="fermer la barre de recherche"
                  onClick={() => searchOpeningHandler(false)}
                  className={classes.searchClose}
                >
                  X
                </span>
              </Grid>
            )}
            {!mobileSearchOpen && <AccountInfo />}
          </Hidden>
        </Grid>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
