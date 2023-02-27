import React, { useState } from 'react';

import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';

import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';

import AccountInfo from './AccountInfo';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import Search from './Search';
import Logo from './Logo';

const MobileTopBar = () => {
  const { options } = useCurrentPoll();

  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  const searchOpeningHandler = (open: boolean) => {
    setMobileSearchOpen(open);
  };

  return (
    <>
      {mobileSearchOpen ? (
        <Grid container width="100%" px={1} justifyContent="center">
          <Grid item xs={11} sm={8}>
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
      ) : (
        <>
          <Logo />
          <IconButton
            aria-label="Open the searchbar"
            onClick={() => searchOpeningHandler(true)}
          >
            <SearchIcon fontSize="large" />
          </IconButton>
          <AccountInfo />
        </>
      )}
    </>
  );
};

export default MobileTopBar;
