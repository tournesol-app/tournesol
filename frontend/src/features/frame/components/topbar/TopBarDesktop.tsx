import React from 'react';

import Grid from '@mui/material/Grid';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import AccountInfo from './AccountInfo';
import Search from './Search';
import Logo from './Logo';

const TopBarDesktop = () => {
  const { options } = useCurrentPoll();

  return (
    <>
      <Logo />
      <Grid item md={4}>
        {options?.withSearchBar && <Search />}
      </Grid>
      <AccountInfo />
    </>
  );
};

export default TopBarDesktop;
