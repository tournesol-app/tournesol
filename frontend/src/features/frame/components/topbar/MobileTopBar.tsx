import React, { useState } from 'react';

import { Grid, IconButton } from '@mui/material';
import { Close, Search } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import AccountInfo from './AccountInfo';
import Logo from './Logo';
import { default as SearchBar } from './Search';

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
          <Grid item xs={11}>
            {options?.withSearchBar && <SearchBar />}
          </Grid>
          <Grid item xs={1}>
            <IconButton
              aria-label="Close the searchbar"
              onClick={() => searchOpeningHandler(false)}
            >
              <Close />
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
            <Search fontSize="large" />
          </IconButton>
          <AccountInfo />
        </>
      )}
    </>
  );
};

export default MobileTopBar;
