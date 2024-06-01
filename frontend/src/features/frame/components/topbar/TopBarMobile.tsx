import React, { useState } from 'react';

import { Box, Grid, IconButton } from '@mui/material';
import { Search, Undo } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import AccountInfo from './AccountInfo';
import Logo from './Logo';
import { default as SearchBar } from './Search';

/**
 * Contrary to `<TopBarDesktop>`, this component displays the search bar only
 * if the user clicks on the search button.
 */
const TopBarMobile = () => {
  const { options } = useCurrentPoll();

  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  const searchOpeningHandler = (open: boolean) => {
    setMobileSearchOpen(open);
  };

  return (
    <>
      {mobileSearchOpen ? (
        <Grid
          container
          width="100%"
          px={1}
          spacing={2}
          justifyContent="flex-start"
        >
          <Grid item xs={11}>
            {options?.withSearchBar && <SearchBar />}
          </Grid>
          <Grid item xs={1}>
            <Box display="flex" justifyContent="center">
              <IconButton
                aria-label="Close the searchbar"
                onClick={() => searchOpeningHandler(false)}
              >
                <Undo />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      ) : (
        <>
          <Logo />
          <Grid item>
            <IconButton
              aria-label="Open the searchbar"
              onClick={() => searchOpeningHandler(true)}
            >
              <Search fontSize="large" />
            </IconButton>
          </Grid>
          <AccountInfo />
        </>
      )}
    </>
  );
};

export default TopBarMobile;
