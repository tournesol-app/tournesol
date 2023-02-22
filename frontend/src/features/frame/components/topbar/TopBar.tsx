import React, { useState } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import AppBar from '@mui/material/AppBar';
import Grid from '@mui/material/Grid';
import Hidden from '@mui/material/Hidden';
import IconButton from '@mui/material/IconButton';
import Toolbar from '@mui/material/Toolbar';

import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
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
      xs={'auto'}
      marginRight="auto"
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
              <IconButton
                aria-label="Open the searchbar"
                onClick={() => searchOpeningHandler(true)}
              >
                <SearchIcon fontSize="large" />
              </IconButton>
            )}
            {mobileSearchOpen && (
              <Grid container width="100%">
                <Grid item xs={11}>
                  {options?.withSearchBar && <Search />}
                </Grid>
                <Grid item xs={1}>
                  <IconButton
                    aria-label="Close the searchbar"
                    onClick={() => searchOpeningHandler(false)}
                  >
                    <CloseIcon />
                  </IconButton>
                </Grid>
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
