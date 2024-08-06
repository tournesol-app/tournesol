import React from 'react';

import Grid from '@mui/material/Grid';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import AccountInfo from './AccountInfo';
import Logo from './Logo';
import Search from './Search';

const TopBarDesktop = () => {
  const { options } = useCurrentPoll();

  return (
    <>
      <Logo />
      <Grid item xs>
        {options?.withSearchBar && <Search />}
      </Grid>
      <AccountInfo />
    </>
  );
};

export default TopBarDesktop;
